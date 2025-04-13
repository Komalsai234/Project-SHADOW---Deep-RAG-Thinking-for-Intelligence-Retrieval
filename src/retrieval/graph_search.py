from typing import List, Dict
from src.ingestion.storage import HybridStorage
import networkx as nx
import logging

logging.basicConfig(level=logging.INFO)

class GraphSearch:
    def __init__(self):
        self.storage = HybridStorage()

    def search(self, query: str, agent_level: int, top_k: int = 5) -> List[Dict]:
        try:
            graph = self.storage.graph
            if not graph or graph.number_of_nodes() == 0:
                logging.warning("Graph is empty, skipping graph search")
                return []

            query_entities = [word.lower() for word in query.split() if word.isalpha() and len(word) > 2]
            logging.info(f"Query entities: {query_entities}")
            results = []
            for node in graph.nodes:
                if graph.nodes[node].get("type") == "chunk":
                    chunk_entities = [e.lower() for e in graph.nodes[node].get("entities", "").split(",") if e.strip()]
                    chunk_clearance = graph.nodes[node].get("clearance", 7)
                    if chunk_clearance <= agent_level:
                        overlap = len(set(query_entities) & set(chunk_entities))
                        if overlap > 0:
                            results.append({
                                "content": graph.nodes[node]["content"],
                                "metadata": {
                                    "chunk_id": node,
                                    "clearance": chunk_clearance,
                                    "entities": graph.nodes[node].get("entities", "")
                                },
                                "score": overlap / max(len(query_entities), 1),
                                "source": "Secret Info Manual"
                            })
                        logging.debug(f"Chunk {node} entities: {chunk_entities}, overlap: {overlap}")

            sorted_results = sorted(results, key=lambda x: x["score"], reverse=True)[:top_k]
            logging.info(f"Graph search retrieved {len(sorted_results)} results")
            if not sorted_results:
                logging.info("No chunks matched query entities")
            return sorted_results
        except Exception as e:
            logging.error(f"Graph search failed: {str(e)}")
            return []