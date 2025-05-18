from typing import List
from langchain.text_splitter import RecursiveCharacterTextSplitter
from backend.app.langchain.chains import LLMChains
from backend.services.google_drive_loader import GoogleDocLoader
from backend.services.vector_db import VectorDB
from backend.services.gemini_service import GeminiService


class DocumentManager:
    """
    This adapter class coordinates interactions between different services for document processing,
    including Google Doc loading, storing content in a vector DB, and utilizing LLM (GeminiService).
    """

    def __init__(self):
        self.google_doc_loader = GoogleDocLoader()
        self.vector_db = VectorDB()
        self.gemini_service = GeminiService()
        self.llm_chains = LLMChains()

    def load_and_store_document(self, doc_link: str, collection: str, user_id: str) -> None:
        """
        Loads the document from Google Docs, extracts its content, and stores it in the vector database.

        Args:
            doc_link (str): The URL of the Google Document.
            collection (str): The name of the vector database collection.
            user_id (str): The unique identifier of the user.
        """
        # Get content of Google document
        doc_content = self.google_doc_loader.load_document(doc_link)

        # Splits document content by 'Feature X:' blocks
        regex_separator = r"(Feature \d+:.*?)(?=\n\s*Feature \d+:|\Z)"
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000000,
            chunk_overlap=0,
            separators=[regex_separator],
            is_separator_regex=True
        )
        chunks_to_store = text_splitter.split_text(doc_content)

        # Embed split features (chunks)
        embeddings = self.embed_content(content=chunks_to_store, task_type='retrieval_document')

        # Create list of unique IDs for each document chunk
        doc_ids = [f"{user_id}_{collection}_f{i}" for i in range(len(chunks_to_store))]

        # Create list of metadata dictionaries for each document chunk (to filter by user ID)
        metadata = [{"user_id": user_id} for _ in chunks_to_store]

        # Save the document content in the vector database
        self.vector_db.store_data(chunks=chunks_to_store, embeddings=embeddings,
                                  doc_ids=doc_ids, collection=collection, metadata=metadata)

    def embed_content(self, content: str | List[str], task_type: str) -> List[List[float]] | List[float]:
        """
        Generates embeddings for the given content.

        Args:
            content (str | List[str]): The text to embed (can be a single string or a list of strings).
            task_type (str): The type of embedding task.

        Returns:
            List[List[float]] | List[float]: A list of vector embeddings for the provided content.
        """
        return self.gemini_service.embed_content(content=content, task_type=task_type)

    def find_similar_data_to_query(self, query: str, collection: str, user_id: str) -> List[str]:
        """
        Searches the vector database for data similar to the given query.

        Args:
            query (str): The search query text.
            collection (str): The name of the vector database collection.
            user_id (str): The unique identifier of the user.

        Returns:
            List[str]: A list of found similar data.
        """
        query_embedding = self.embed_content(content=query, task_type='retrieval_query')
        metadata = {"user_id": user_id}
        return self.vector_db.retrieve_relevant_data(
            query_embedding=query_embedding, collection=collection, metadata=metadata
        )

    def generate_test_cases(self, relevant_specs: List[str], relevant_test_cases: List[str], feature: str) -> str:
        """
        Generates test cases by LLM based on the provided specification, existing test cases, and user request.

        Args:
            relevant_specs (List[str]): A list of specification chunks related to the feature.
            relevant_test_cases (List[str]): A list of existing test cases related to the feature.
            feature (str): The specific feature for which test cases need to be generated.

        Returns:
            str: The generated test cases in text format, including appropriate HTML tags for formatting.
                 If no relevant test cases are found, an error message is returned.
        """
        specification = '\n'.join(relevant_specs)
        test_cases = '\n'.join(relevant_test_cases)

        chain = self.llm_chains.build_test_case_chain()
        result = chain.invoke({
            "specification": specification,
            "test_cases": test_cases,
            "feature": feature
        })

        return result.content
