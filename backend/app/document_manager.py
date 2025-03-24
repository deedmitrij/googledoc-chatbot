import re
from typing import List
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

        # Find all the features and split the content
        feature_pattern = r"(Feature \d+:.*?)(?=\n\s*Feature \d+:|\Z)"
        chunks_to_store = re.findall(feature_pattern, doc_content, re.DOTALL)

        # Embed split features (chunks)
        embeddings = self.embed_content(content=chunks_to_store, task_type='retrieval_document')

        # Create list of unique IDs for each document chunk
        doc_ids = [f"{user_id}_{collection}_f{i}" for i in range(len(chunks_to_store))]

        # Create list of metadata dictionaries for each document chunk (to filter by user ID)
        metadata = [{"user_id": user_id} for _ in chunks_to_store]

        # Save the document content in the vector database
        self.vector_db.store_data(chunks=chunks_to_store, embeddings=embeddings,
                                  doc_ids=doc_ids, collection=collection, metadata=metadata)

    def embed_content(self, content: str | List[str], task_type: str) -> List[List[float]] | [List[float]]:
        """
        Generates embeddings for the given content.

        Args:
            content (str | List[str]): The text to embed (can be a single string or a list of strings).
            task_type (str): The type of embedding task.

        Returns:
            List[List[float]] | [List[float]]: A list of vector embeddings for the provided content.
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

        # Combine relevant documents into a single text block
        specification = '\n'.join(relevant_specs)
        test_cases = '\n'.join(relevant_test_cases)

        # Construct the prompt for the LLM
        prompt = f"""
        You are an expert in software testing and quality assurance.
        Your task is to analyze the provided **software specification** and **existing test cases** 
        to generate suite of relevant test cases for the **user query**.

        ### **User query to analyze:**
        **"{feature}"**

        ### **Input Documents:**  
        - **Specification:**  
        "{specification}"

        - **Existing Test Cases:**  
        "{test_cases}"

        ---

        ### **Instructions:**  
        1. Return only the test cases that are **specifically related to the user query**.
        2. If there are **existing test cases** related to the user query, 
           return them as they are or update them if it is necessary according to the specification.
        3. If no existing test cases found, **generate new test cases** based on the specification.
        4. Generate test cases only by strictly following the requirements in the specification. 
           Do not think up additional functionality if it is not specified in the requirements. 
           If the specification specifies functionality that has not been implemented yet, only in plans, 
           ignore it and do not add it to test cases.
        5. Do not duplicate checks in different test cases. Try to cover the specification with unique test cases.
        6. Divide the tests into positive and negative tests, starting with the positive ones.
        7. Always start you answer with the phrase "Here are test cases for" adding further what the user requested for 
           and then provide the suite of generated test cases.
        8. If it is not possible to generate test cases at the user's query 
           according to the specification or due to absence of specification 
           (which means that no relevant documentation was found for the user's query), 
           return a response starting with "⚠️ Error" adding further the reason 
           why it is not possible to generate test cases.
        9. Output format must be as normal text, but including appropriate HTML tags 
           in the places of line breaks, paragraph breaks, text highlighting, lists, etc. Example:
           "
           <h3>Test Case 4: Verify the sorting functionality (e.g., sort by price low to high)</h3>
           <p><strong>Test Steps:</strong></p>
           <ol>
             <li>Open the homepage.</li>
             <li>Select the “Sort by Price: Low to High” option from the sorting dropdown.</li>
             <li>Click on the “Apply Sort” button.</li>
           </ol>
           <p><strong>Expected Result:</strong></p>
           <p>Products are sorted in ascending order of price.</p>
           "

        ---

        Now, analyze the provided information and generate the most relevant test cases.
        """

        return self.gemini_service.generate_content(prompt=prompt)
