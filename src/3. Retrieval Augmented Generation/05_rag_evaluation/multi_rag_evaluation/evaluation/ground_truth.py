from langchain_community.document_loaders import DirectoryLoader

class GroundTruthGenerator:
    """Generate expert-level ground truth answers for evaluation."""

    def __init__(self, expert_llm):
        self.expert_llm = expert_llm

    def generate_ground_truths(self, questions, data_dir):
        """Generate ground truth answers using expert LLM with complete context."""
        loader = DirectoryLoader(data_dir, glob="*.txt")
        docs = loader.load()
        full_context = "\n\n".join([doc.page_content for doc in docs])

        ground_truths = []
        for question in questions:
            prompt = f"""You are a domain expert with complete knowledge of these scientists.
Based on the following complete biographies, provide a comprehensive, accurate answer.

Complete Biographies:
{full_context}

Question: {question}

Provide a detailed, factually accurate answer:"""

            answer = self.expert_llm.invoke(prompt).content
            ground_truths.append(answer)

        return ground_truths