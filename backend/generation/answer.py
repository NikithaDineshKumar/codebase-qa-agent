import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage

load_dotenv()

# Initialize Gemini model
llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    google_api_key=os.getenv("GOOGLE_API_KEY"),
    temperature=0.2,
)

SYSTEM_PROMPT = """You are an expert code assistant that helps developers understand codebases.
You are given relevant code chunks retrieved from a repository and a user question.
Your job is to answer the question accurately based on the provided code context.

Guidelines:
- Always reference specific file paths and line numbers when explaining code
- If the answer spans multiple files, explain the flow clearly
- If the context is insufficient, say so honestly
- Format code snippets using markdown code blocks
- Be concise but thorough
"""

def generate_answer(query: str, context_chunks: list[dict]) -> dict:
    """
    Generates an answer using Gemini based on retrieved code chunks.
    Returns answer text and source references.
    """
    # Build context string from chunks
    context = ""
    for i, chunk in enumerate(context_chunks):
        context += f"\n--- Chunk {i+1} ---\n"
        context += f"File: {chunk['file_path']}\n"
        context += f"Lines: {chunk['start_line']} - {chunk['end_line']}\n"
        context += f"Type: {chunk['chunk_type']} | Name: {chunk['name']}\n"
        context += f"Code:\n{chunk['content']}\n"

    user_message = f"""Based on the following code context, answer this question:

Question: {query}

Code Context:
{context}

Answer:"""

    messages = [
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=user_message),
    ]

    response = llm.invoke(messages)

    # Build source references
    sources = []
    for chunk in context_chunks:
        sources.append({
            "file_path": chunk["file_path"],
            "start_line": chunk["start_line"],
            "end_line": chunk["end_line"],
            "name": chunk["name"],
            "chunk_type": chunk["chunk_type"],
            "rrf_score": chunk.get("rrf_score", 0),
        })

    return {
        "answer": response.content,
        "sources": sources,
        "total_chunks_used": len(context_chunks),
    }