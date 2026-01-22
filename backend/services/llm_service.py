from openai import OpenAI
from typing import List
from langchain_openai import ChatOpenAI
from huggingface_hub import InferenceClient
from config import HF_API_KEY


class LLMService:
    """Handles AI interactions with LLM."""

    def __init__(self):
        hf_url = "https://router.huggingface.co/v1"
        self.model = "Qwen/Qwen2.5-7B-Instruct"
        self.embedding_model = "BAAI/bge-small-en-v1.5"
        self.chat_client = OpenAI(api_key=HF_API_KEY, base_url=hf_url)
        self.inference_client = InferenceClient(api_key=HF_API_KEY)
        self.langchain_model = ChatOpenAI(
            model=self.model,
            openai_api_key=HF_API_KEY,
            openai_api_base=hf_url,
            temperature=0.3,
            max_tokens=2048,
        )

    def generate_content(self, prompt: str) -> str:
        """
        Generates content for the given prompt.

        Args:
            prompt (str): The input prompt to generate text.

        Returns:
            str: The generated content.
        """
        try:
            response = self.chat_client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"},
                max_tokens=1000,
                temperature=0.1
            )
            content = response.choices[0].message.content.strip()
            return content
        except Exception as e:
            return f"⚠️ Error processing request: {str(e)}"

    def embed_content(self, content: str | List[str], task_type: str) -> List[List[float]] | List[float]:
        """
        Generates embeddings for the given content.

        Args:
            content (str): The text to embed.
            task_type (str): The embedding type.

        Returns:
            List[List[float]] | List[float]: A list representing the content's embedding.
        """
        prefixes = {
            "RETRIEVAL_QUERY": "query: ",
            "RETRIEVAL_DOCUMENT": "passage: "
        }

        prefix = prefixes.get(task_type, "")

        input_data = [content] if isinstance(content, str) else content
        input_with_prefix = [f"{prefix}{text}" for text in input_data]

        try:
            embeddings = self.inference_client.feature_extraction(
                input_with_prefix,
                model=self.embedding_model
            )

            # Convert to list of lists if it returns a numpy-like structure
            return embeddings.tolist() if hasattr(embeddings, "tolist") else embeddings
        except Exception as e:
            print(f"⚠️ Embedding Error: {str(e)}")
            return []
