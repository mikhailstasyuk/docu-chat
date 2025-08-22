import os
from typing import List, Dict, Tuple
from openai import AsyncOpenAI
from .weaviate_service import WeaviateService

SYSTEM_PROMPT = """You are a helpful AI assistant. You will answer the user's question based ONLY on the provided context. If the answer is not in the context, say 'I do not have enough information to answer that.'"""

class RAGService:
    """
    Orchestrates the Retrieval-Augmented Generation process.
    """
    def __init__(self, weaviate_service: WeaviateService):
        """
        Initializes the RAG service with a Weaviate service instance.
        """
        self.weaviate_service = weaviate_service
        self.openai_client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.chat_model = "gpt-4o-mini"

    async def get_answer(self, query: str, history: List[Dict[str, str]]) -> Tuple[str, bool]:
        """
        Retrieves context, builds a prompt, and generates an answer.
        Returns the answer and a boolean indicating if context was found.
        """
        # 1. Retrieve relevant chunks
        retrieved_chunks = await self.weaviate_service.query_chunks(query)

        # 2. Hardcoded Guardrail
        if not retrieved_chunks:
            return "I could not find relevant information in the document.", False

        # 3. Construct the prompt
        context_str = "\n---\n".join(retrieved_chunks)
        
        history_str = "\n".join([f"{msg['role']}: {msg['content']}" for msg in history])

        user_prompt = f"""
        Context:
        {context_str}
        
        Conversation History:
        {history_str}

        Based on the context and history above, please answer the following question: {query}
        """

        # 4. Call the OpenAI chat completions API
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt}
        ]

        response = await self.openai_client.chat.completions.create(
            model=self.chat_model,
            messages=messages,
            temperature=0.1, 
        )

        answer = response.choices[0].message.content
        return answer, True