import pandas as pd
from typing import List
from ragas import evaluate, EvaluationDataset
from ragas.metrics import ContextPrecision, ContextRecall, Faithfulness, AnswerRelevancy, FactualCorrectness
from ragas.llms import LangchainLLMWrapper
from ragas.dataset_schema import SingleTurnSample

from .ground_truth import GroundTruthGenerator

class RAGEvaluator:
    """Evaluate and compare multiple RAG systems using RAGAS metrics."""

    def __init__(self, expert_llm, evaluator_llm):
        self.expert_llm = expert_llm
        self.evaluator_llm = evaluator_llm
        self.ground_truth_generator = GroundTruthGenerator(expert_llm)

        # Initialize RAGAS metrics
        wrapped_evaluator = LangchainLLMWrapper(evaluator_llm)
        self.metrics = [
            ContextPrecision(llm=wrapped_evaluator),
            ContextRecall(llm=wrapped_evaluator),
            Faithfulness(llm=wrapped_evaluator),
            AnswerRelevancy(llm=wrapped_evaluator),
            FactualCorrectness(llm=wrapped_evaluator)
        ]

    def evaluate_single_rag(self, rag_system, questions, ground_truths):
        """Evaluate a single RAG system."""
        print(f"   Evaluating {rag_system.name}...")

        # Generate samples
        samples = []
        for question, ground_truth in zip(questions, ground_truths):
            try:
                answer, contexts = rag_system.query(question)
                samples.append(SingleTurnSample(
                    user_input=question,
                    response=answer,
                    retrieved_contexts=contexts,
                    reference=ground_truth
                ))
            except Exception as e:
                print(f"   Warning: Failed to query {rag_system.name} for '{question}': {e}")
                continue

        if not samples:
            print(f"   Error: No valid samples for {rag_system.name}")
            return None

        # Create evaluation dataset
        eval_dataset = EvaluationDataset(samples=samples)

        # Run evaluation
        try:
            result = evaluate(dataset=eval_dataset, metrics=self.metrics)
            return result
        except Exception as e:
            print(f"   Error evaluating {rag_system.name}: {e}")
            return None

    def compare_systems(self, rag_systems, questions, data_dir):
        """Compare multiple RAG systems."""
        print("Generating ground truths with expert LLM...")
        ground_truths = self.ground_truth_generator.generate_ground_truths(questions, data_dir)
        print("✓ Ground truths generated")

        results = {}

        for rag_system in rag_systems:
            result = self.evaluate_single_rag(rag_system, questions, ground_truths)
            if result is not None:
                results[rag_system.name] = result

        return results

    def create_comparison_dataframe(self, results):
        """Create a comparison DataFrame from evaluation results."""
        comparison_data = []

        for system_name, result in results.items():
            df = result.to_pandas()

            # Calculate average scores for each metric
            metric_scores = {}
            metric_names = [col for col in df.columns if col not in
                          ['user_input', 'response', 'retrieved_contexts', 'reference']]

            for metric_name in metric_names:
                if metric_name in df.columns:
                    metric_scores[metric_name] = df[metric_name].mean()

            metric_scores['system'] = system_name
            comparison_data.append(metric_scores)

        return pd.DataFrame(comparison_data)

    def print_comparison_table(self, comparison_df):
        """Print a formatted comparison table."""
        if comparison_df.empty:
            print("No results to display")
            return

        print("\n" + "="*80)
        print("COMPARATIVE EVALUATION RESULTS")
        print("="*80)

        # Reorder columns for better display
        display_cols = ['system']
        metric_cols = [col for col in comparison_df.columns if col != 'system']
        display_cols.extend(sorted(metric_cols))

        display_df = comparison_df[display_cols].round(3)

        # Format column names for display
        display_df.columns = [col.replace('_', ' ').title() if col != 'system' else 'System'
                             for col in display_df.columns]

        print(display_df.to_string(index=False))

        # Find best performing system per metric
        print("\n" + "-"*80)
        print("BEST PERFORMERS:")
        for col in metric_cols:
            if col in comparison_df.columns:
                best_system = comparison_df.loc[comparison_df[col].idxmax(), 'system']
                best_score = comparison_df[col].max()
                print(f"• {col.replace('_', ' ').title()}: {best_system} ({best_score:.3f})")

        # Calculate overall best (average of all metrics)
        metric_means = comparison_df[metric_cols].mean(axis=1)
        overall_best_idx = metric_means.idxmax()
        overall_best = comparison_df.loc[overall_best_idx, 'system']
        overall_score = metric_means[overall_best_idx]
        print(f"• Overall Best: {overall_best} (Avg: {overall_score:.3f})")

    def save_results(self, comparison_df, results_dir="results"):
        """Save detailed results to files."""
        import os
        os.makedirs(results_dir, exist_ok=True)

        # Save comparison table
        comparison_df.to_csv(f"{results_dir}/comparison_metrics.csv", index=False)

        print(f"\n✓ Results saved to {results_dir}/comparison_metrics.csv")