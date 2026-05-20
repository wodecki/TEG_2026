#!/usr/bin/env python3
"""
Ground Truth Generator for GraphRAG vs Naive RAG Comparison
==========================================================

Uses GPT-4.1 with full CV context to generate authoritative answers
for test questions. This provides an independent, unbiased ground truth
for evaluating both GraphRAG and Naive RAG systems.

Configuration:
- Processes all 30 CVs by default (change max_cvs in __init__ to limit)
- Processes all 42 questions by default (pass max_questions to generate_all_ground_truths to limit)
- Includes detailed timing diagnostics
"""

from dotenv import load_dotenv
load_dotenv(override=True)

import os
import json
import asyncio
from pathlib import Path
from typing import List, Dict, Any
import logging
from langchain_openai import ChatOpenAI
from langchain_community.document_loaders import PyPDFLoader
from langchain_core.prompts import PromptTemplate

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GroundTruthGenerator:
    """Generate ground truth answers using GPT-5 with full CV context."""

    def __init__(self, max_cvs: int = 30):
        """Initialize the ground truth generator."""
        # Use GPT-4.1 for performance comparison
        self.llm = ChatOpenAI(
            model="gpt-4.1",
            max_tokens=4096,
            api_key=os.getenv("OPENAI_API_KEY")
        )

        # Directories
        self.data_dir = Path("data/programmers")
        self.results_dir = Path("results")
        self.results_dir.mkdir(exist_ok=True)

        # Limit number of CVs for testing
        self.max_cvs = max_cvs

        logger.info(f"✓ GPT-4.1 Ground Truth Generator initialized (using {max_cvs} CVs)")

    def load_all_cvs(self) -> List[str]:
        """Load all CV PDFs and extract text content."""
        cv_texts = []
        cv_files = list(self.data_dir.glob("*.pdf"))

        if not cv_files:
            raise FileNotFoundError(f"No PDF files found in {self.data_dir}")

        # Limit to max_cvs
        cv_files = sorted(cv_files)[:self.max_cvs]
        logger.info(f"Loading {len(cv_files)} CV files...")

        for cv_file in cv_files:
            try:
                loader = PyPDFLoader(str(cv_file))
                documents = loader.load()

                # Combine all pages into single text
                cv_text = "\n".join([doc.page_content for doc in documents])
                cv_texts.append(f"=== CV: {cv_file.stem} ===\n{cv_text}")

            except Exception as e:
                logger.warning(f"Could not load {cv_file}: {e}")
                continue

        logger.info(f"✓ Successfully loaded {len(cv_texts)} CVs")
        return cv_texts

    def create_ground_truth_prompt(self) -> PromptTemplate:
        """Create the prompt template for ground truth generation."""
        template = """You are a senior HR manager with exceptional analytical skills and perfect memory.
You have been given ALL {num_cvs} CVs from our candidate database to review comprehensively.

Your task is to answer the following question with ABSOLUTE PRECISION and COMPLETENESS based on the CVs provided.

CRITICAL INSTRUCTIONS:
- Provide ONLY the direct answer, no explanations or reasoning
- For counting questions: Give only the number (e.g., "3" or "Zero")
- For listing questions: List only the names, comma-separated
- For aggregation questions: Give only the calculated result
- For filtering questions: List only the matching names, comma-separated
- For ranking questions: List names in order, comma-separated
- Be specific with names, skills, companies, and other details
- If no matches: answer "None" or "Zero" as appropriate
- MAXIMUM 1-2 sentences, be extremely concise

CVs Database ({num_cvs} total CVs):
{context}

Question: {question}

Answer (concise, direct):"""

        return PromptTemplate(
            input_variables=["num_cvs", "context", "question"],
            template=template
        )

    async def generate_ground_truth_for_question(self, question: str, all_cv_texts: List[str]) -> Dict[str, Any]:
        """Generate ground truth answer for a single question."""
        import time
        start_time = time.time()

        try:
            # Combine all CVs into context
            context_build_start = time.time()
            full_context = "\n\n" + "="*80 + "\n\n".join(all_cv_texts)
            context_build_time = time.time() - context_build_start

            # Check context size (rough estimate)
            context_tokens = len(full_context.split()) * 1.3  # Rough token estimate
            logger.info(f"Context size: ~{context_tokens:,.0f} tokens (built in {context_build_time:.2f}s)")

            if context_tokens > 300000:  # Conservative limit for GPT-5
                logger.warning(f"Context size may be large: {context_tokens:,.0f} tokens")

            # Create prompt
            prompt_template = self.create_ground_truth_prompt()
            prompt = prompt_template.format(
                num_cvs=len(all_cv_texts),
                context=full_context,
                question=question
            )

            # Generate answer with GPT-5
            logger.info(f"Calling API for: {question[:60]}...")
            api_start = time.time()
            response = await self.llm.ainvoke(prompt)
            api_time = time.time() - api_start

            ground_truth_answer = response.content.strip()

            total_time = time.time() - start_time
            logger.info(f"✓ Generated in {total_time:.2f}s (API: {api_time:.2f}s, {len(ground_truth_answer)} chars)")

            return {
                "question": question,
                "ground_truth_answer": ground_truth_answer,
                "context_tokens_estimate": int(context_tokens),
                "num_cvs_used": len(all_cv_texts),
                "model_used": "gpt-4.1",
                "status": "success",
                "generation_time_seconds": total_time,
                "api_time_seconds": api_time
            }

        except Exception as e:
            total_time = time.time() - start_time
            logger.error(f"Error generating ground truth for '{question}': {e}")

            return {
                "question": question,
                "ground_truth_answer": f"ERROR: {str(e)}",
                "context_tokens_estimate": 0,
                "num_cvs_used": len(all_cv_texts),
                "model_used": "gpt-4.1",
                "status": "error",
                "error": str(e),
                "generation_time_seconds": total_time
            }

    def load_test_questions(self) -> Dict[str, Any]:
        """Load test questions from JSON file."""
        questions_file = Path(__file__).parent / "test_questions.json"
        if not questions_file.exists():
            raise FileNotFoundError(f"Test questions file not found: {questions_file}")

        with open(questions_file, 'r') as f:
            return json.load(f)

    async def generate_all_ground_truths(self, max_questions: int = None) -> Dict[str, Any]:
        """Generate ground truth answers for all test questions."""
        # Load CVs and questions
        all_cv_texts = self.load_all_cvs()
        test_data = self.load_test_questions()

        # Extract all questions from all categories
        all_questions = []
        for category_name, category_data in test_data["test_suite"]["categories"].items():
            for question in category_data["questions"]:
                all_questions.append({
                    "question": question,
                    "category": category_name,
                    "description": category_data["description"]
                })

        # Limit number of questions if specified
        if max_questions:
            all_questions = all_questions[:max_questions]
            logger.info(f"Generating ground truth for {len(all_questions)} questions (limited from {len(all_questions)} total)")
        else:
            logger.info(f"Generating ground truth for all {len(all_questions)} questions...")

        # Generate ground truth for each question
        results = []
        for i, question_data in enumerate(all_questions):
            question = question_data["question"]
            category = question_data["category"]

            logger.info(f"\n[{i+1}/{len(all_questions)}] Processing {category}: {question}")

            # Generate ground truth
            result = await self.generate_ground_truth_for_question(question, all_cv_texts)
            result["category"] = category
            result["category_description"] = question_data["description"]
            result["question_index"] = i + 1

            results.append(result)

            # Small delay to respect rate limits
            await asyncio.sleep(1)

        # Compile final results
        ground_truth_data = {
            "metadata": {
                "generated_by": "GroundTruthGenerator",
                "model": "gpt-4.1",
                "num_questions": len(results),
                "num_cvs": len(all_cv_texts),
                "cv_source_dir": str(self.data_dir),
                "total_successful": len([r for r in results if r["status"] == "success"]),
                "total_errors": len([r for r in results if r["status"] == "error"])
            },
            "ground_truth_answers": results,
            "original_test_questions": test_data
        }

        return ground_truth_data

    def save_ground_truth(self, ground_truth_data: Dict[str, Any]) -> Path:
        """Save ground truth data to JSON file."""
        output_file = self.results_dir / "ground_truth_answers.json"

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(ground_truth_data, f, indent=2, ensure_ascii=False)

        logger.info(f"✓ Ground truth saved to: {output_file}")
        return output_file

    def display_summary(self, ground_truth_data: Dict[str, Any]) -> None:
        """Display a summary of the ground truth generation."""
        metadata = ground_truth_data["metadata"]
        results = ground_truth_data["ground_truth_answers"]

        print("\n" + "="*60)
        print("Ground Truth Generation Summary")
        print("="*60)
        print(f"Model Used: {metadata['model']}")
        print(f"Total Questions: {metadata['num_questions']}")
        print(f"CVs Analyzed: {metadata['num_cvs']}")
        print(f"Successful: {metadata['total_successful']}")
        print(f"Errors: {metadata['total_errors']}")

        # DIAGNOSTIC: Show timing statistics
        successful_results = [r for r in results if r["status"] == "success" and "generation_time_seconds" in r]
        if successful_results:
            total_time = sum(r["generation_time_seconds"] for r in successful_results)
            avg_time = total_time / len(successful_results)
            api_times = [r.get("api_time_seconds", 0) for r in successful_results]
            avg_api_time = sum(api_times) / len(api_times) if api_times else 0

            print(f"\n⏱️  TIMING DIAGNOSTICS:")
            print(f"Total generation time: {total_time:.2f}s ({total_time/60:.2f} minutes)")
            print(f"Average per question: {avg_time:.2f}s")
            print(f"Average API time: {avg_api_time:.2f}s")

        # Show category breakdown
        print(f"\nQuestions by Category:")
        categories = {}
        for result in results:
            cat = result["category"]
            categories[cat] = categories.get(cat, 0) + 1

        for category, count in categories.items():
            print(f"  • {category}: {count} questions")

        # Show sample ground truth
        print(f"\nSample Ground Truth Answers:")
        for result in results[:3]:
            if result["status"] == "success":
                answer = result["ground_truth_answer"]
                truncated = answer[:100] + "..." if len(answer) > 100 else answer
                print(f"\nQ: {result['question']}")
                print(f"A: {truncated}")

        print("\n" + "="*60)


async def main():
    """Main function to generate ground truth answers."""
    print("Ground Truth Generator for GraphRAG vs Naive RAG Comparison")
    print("=" * 65)

    try:
        generator = GroundTruthGenerator()

        # Generate all ground truths
        ground_truth_data = await generator.generate_all_ground_truths()

        # Save results
        output_file = generator.save_ground_truth(ground_truth_data)

        # Display summary
        generator.display_summary(ground_truth_data)

        print(f"\n🎉 Ground truth generation complete!")
        print(f"📁 Results saved to: {output_file}")
        print(f"\nNext steps:")
        print(f"1. Create naive RAG baseline: uv run python 4_naive_rag_cv.py")
        print(f"2. Run comparison: uv run python 5_compare_systems.py")

    except Exception as e:
        logger.error(f"Ground truth generation failed: {e}")
        print(f"\n❌ Error: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(main())