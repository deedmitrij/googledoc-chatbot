import google.generativeai as genai
from typing import List
from backend.config import GEMINI_API_KEY


class GeminiService:
    """Handles AI interactions with Google Gemini."""

    def __init__(self):
        genai.configure(api_key=GEMINI_API_KEY)
        self.model = genai.GenerativeModel("gemini-1.5-flash")

    def generate_content(self, prompt: str) -> str:
        """
        Generates content for the given prompt.

        Args:
            prompt (str): The input prompt to generate text.

        Returns:
            str: The generated content.
        """
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"⚠️ Error processing request: {str(e)}"

    @staticmethod
    def embed_content(content: str | List[str], task_type: str) -> List[List[float]] | List[float]:
        """
        Generates embeddings for the given content.

        Args:
            content (str): The text to embed.
            task_type (str): The embedding type.

        Returns:
            List[List[float]] | List[float]: A list representing the content's embedding.
        """
        response = genai.embed_content(model="models/embedding-001", content=content, task_type=task_type)
        return response["embedding"]
