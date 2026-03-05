from dotenv import load_dotenv
load_dotenv(override=True)

import os
import json
from pathlib import Path
from langchain_community.document_loaders import DirectoryLoader
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain.text_splitter import RecursiveCharacterTextSplitter
from ragas import evaluate, EvaluationDataset
from ragas.metrics import ContextPrecision, ContextRecall, Faithfulness, AnswerRelevancy, FactualCorrectness
from ragas.llms import LangchainLLMWrapper
from ragas.dataset_schema import SingleTurnSample

def load_and_chunk(data_dir):
    loader = DirectoryLoader(data_dir, glob="*.txt")
    docs = loader.load()
    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    return splitter.split_documents(docs)

def build_rag_system(chunks):
    embeddings = OpenAIEmbeddings()
    vector_store = InMemoryVectorStore(embeddings)
    vector_store.add_documents(documents=chunks)

    retriever = vector_store.as_retriever(
        search_type="similarity",
        search_kwargs={"k": 3}
    )

    llm = ChatOpenAI(model="gpt-4o-mini")

    prompt = ChatPromptTemplate.from_template("""
You are an assistant for question-answering tasks.
Use the following pieces of retrieved context to answer the question.
If you don't know the answer, just say that you don't know.
Use three sentences maximum and keep the answer concise.

Question: {question}

Context: {context}

Answer:
""")

    rag_chain = (
        {"context": retriever, "question": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    )

    return rag_chain, retriever

def generate_ground_truths(questions, data_dir, expert_llm):
    loader = DirectoryLoader(data_dir, glob="*.txt")
    docs = loader.load()
    full_context = "\n\n".join([doc.page_content for doc in docs])

    ground_truths = []
    for q in questions:
        prompt = f"""You are a domain expert with complete knowledge of these scientists.
Based on the following complete biographies, provide a comprehensive, accurate answer.

Complete Biographies:
{full_context}

Question: {q}

Provide a detailed, factually accurate answer:"""
        ground_truths.append(expert_llm.invoke(prompt).content)
    return ground_truths

if not os.getenv("OPENAI_API_KEY"):
    raise ValueError("OPENAI_API_KEY not found in environment")

data_dir = "data/scientists_bios"
if not os.path.exists(data_dir):
    raise FileNotFoundError(f"Data directory not found: {data_dir}")

chunks = load_and_chunk(data_dir)
rag_chain, retriever = build_rag_system(chunks)
expert_llm = ChatOpenAI(model="gpt-5")

questions = [
    "What did Marie Curie win Nobel Prizes for?",
    "What is Einstein's theory of relativity about?",
    "What are Newton's three laws of motion?",
    "What did Charles Darwin discover?",
    "What was Ada Lovelace's contribution to computing?"
]

output_dir = Path("data")
output_file = output_dir / "ground_truth_dataset.json"

if output_file.exists():
    print(f"Loading existing ground truth dataset from {output_file}")
    with open(output_file, "r") as f:
        ground_truth_data = json.load(f)
    ground_truths = [item["ground_truth"] for item in ground_truth_data]
else:
    print("Generating ground truth answers using expert LLM...")
    ground_truths = generate_ground_truths(questions, data_dir, expert_llm)

    output_dir.mkdir(exist_ok=True)
    ground_truth_data = [{"question": q, "ground_truth": gt} for q, gt in zip(questions, ground_truths)]
    with open(output_file, "w") as f:
        json.dump(ground_truth_data, f, indent=2)
    print(f"Ground truth dataset saved to {output_file}")

samples = []
for q, gt in zip(questions, ground_truths):
    answer = rag_chain.invoke(q)
    contexts = [doc.page_content for doc in retriever.invoke(q)]
    samples.append(SingleTurnSample(
        user_input=q,
        response=answer,
        retrieved_contexts=contexts,
        reference=gt
    ))

eval_dataset = EvaluationDataset(samples=samples)

evaluator_llm = LangchainLLMWrapper(ChatOpenAI(model="gpt-4.1", temperature=0))
metrics = [
    ContextPrecision(llm=evaluator_llm),
    ContextRecall(llm=evaluator_llm),
    Faithfulness(llm=evaluator_llm),
    AnswerRelevancy(llm=evaluator_llm),
    FactualCorrectness(llm=evaluator_llm)
]

result = evaluate(dataset=eval_dataset, metrics=metrics)

df = result.to_pandas()
metric_names = [col for col in df.columns if col not in ['user_input', 'response', 'retrieved_contexts', 'reference']]
for metric_name in metric_names:
    score = df[metric_name].mean()
    print(f"{metric_name}: {score:.3f}")