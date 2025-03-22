import numpy as np
import faiss
from typing import List


class VectorDB:  # FAISS
    def __init__(self):
        self.index_store = {}  # indices per collection
        self.doc_store = {}  # {collection: {doc_id: {text, metadata}}}
        self.doc_id_map = {}  # {collection: {faiss_index: doc_id}}

    def store_data(self, chunks: List[str], embeddings: List[List[float]],
                   doc_ids: List[str], metadata: List[dict], collection: str) -> None:
        """
        Stores document data in the vector database.

        Args:
            chunks (List[str]): A list of document chunks to be stored.
            embeddings (List[List[float]]): A list of corresponding embeddings.
            doc_ids (List[str]): A list of unique document identifiers.
            metadata (List[dict]): Metadata associated with each document.
            collection (str): The name of the vector database collection.
        """
        embeddings = np.array(embeddings, dtype=np.float32)

        # Ensure a FAISS index exists for this collection
        if collection not in self.index_store:
            self.index_store[collection] = faiss.IndexIDMap(faiss.IndexFlatL2(embeddings.shape[1]))
            self.doc_id_map[collection] = {}

        index = self.index_store[collection]

        # Assign unique integer FAISS indices to document IDs
        start_idx = len(self.doc_id_map[collection])
        int_ids = np.array(range(start_idx, start_idx + len(doc_ids)), dtype=np.int64)

        index.add_with_ids(embeddings, int_ids)

        # Store document texts and metadata
        if collection not in self.doc_store:
            self.doc_store[collection] = {}

        for i, doc_id in enumerate(doc_ids):
            self.doc_store[collection][doc_id] = {"text": chunks[i], "metadata": metadata[i]}
            self.doc_id_map[collection][start_idx + i] = doc_id  # Map FAISS index → doc_id

    def retrieve_relevant_data(self, query_embedding: List[List[float]], collection: str,
                               metadata: dict, distance_threshold: float = 0.7) -> List[str]:
        """
        Retrieves documents based on FAISS similarity search with distance filtering.

        Args:
            query_embedding (List[List[float]]): The query embedding.
            collection (str): Collection to search in.
            metadata (dict): Metadata filters.
            distance_threshold (float): Maximum L2 distance for relevance.

        Returns:
            List[str]: list of relevant data
        """
        if collection not in self.index_store:
            return []

        index = self.index_store[collection]
        query_embedding = np.array([query_embedding], dtype=np.float32)  # Ensure 2D

        # Search for all potential matches
        num_docs = index.ntotal  # Total stored embeddings
        if num_docs == 0:
            return []

        distances, indices = index.search(query_embedding, num_docs)

        results = []
        seen_doc_ids = set()
        collection_docs = self.doc_store.get(collection, {})

        for i, idx in enumerate(indices[0]):
            if idx == -1 or idx not in self.doc_id_map[collection]:  # Ensure valid FAISS index
                continue

            doc_id = self.doc_id_map[collection][idx]

            if doc_id in seen_doc_ids:  # Avoid duplicates
                continue

            seen_doc_ids.add(doc_id)
            doc_data = collection_docs[doc_id]

            # Apply distance threshold and metadata filtering
            if distances[0][i] <= distance_threshold and all(
                doc_data["metadata"].get(key) == value for key, value in metadata.items()
            ):
                results.append(doc_data["text"])

        return results
