from typing import List, Dict
from src.ingestion.storage import HybridStorage
from sentence_transformers import SentenceTransformer
import logging
import numpy as np

logging.basicConfig(level=logging.INFO)

class VectorSearch:
    def __init__(self):
        self.storage = HybridStorage()
        self.embedding_model = None

    def load_embedding_model(self):
        if self.embedding_model is None:
            logging.info("Loading SentenceTransformer for vector search")
            self.embedding_model = SentenceTransformer("all-MiniLM-L6-v2", trust_remote_code=False)

    def search(self, query: str, agent_level: int, top_k: int = 5) -> List[Dict]:
        self.load_embedding_model()
        try:
            query_embedding = self.embedding_model.encode([query], convert_to_tensor=False, show_progress_bar=False)[0]
            if isinstance(query_embedding, np.ndarray):
                query_embedding = query_embedding.tolist()
            elif not isinstance(query_embedding, list):
                logging.error(f"Invalid query embedding type: {type(query_embedding)}")
                raise ValueError(f"Query embedding is not a list or array: {query_embedding}")

            if not all(isinstance(x, (int, float)) for x in query_embedding):
                logging.error(f"Invalid values in query embedding: {query_embedding}")
                raise ValueError("Query embedding contains non-numeric values")

            logging.info(f"Searching ChromaDB with agent_level: {agent_level}")
            results = self.storage.collection.query(
                query_embeddings=[query_embedding],
                n_results=top_k,
                where={"clearance": {"$lte": agent_level}},
                include=["documents", "metadatas", "distances"]
            )

            formatted_results = []
            if not results["documents"] or not results["documents"][0]:
                logging.info(f"No results found for agent_level: {agent_level}")
                return formatted_results

            for doc, metadata, distance in zip(
                results["documents"][0], results["metadatas"][0], results["distances"][0]
            ):
                formatted_results.append({
                    "content": doc,
                    "metadata": metadata,
                    "score": 1 - distance,
                    "source": metadata.get("doc_id", "Secret Info Manual")
                })
            logging.info(f"Retrieved {len(formatted_results)} results for query")
            return formatted_results
        except Exception as e:
            logging.error(f"Vector search failed: {str(e)}")
            return []