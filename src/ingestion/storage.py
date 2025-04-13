from typing import List, Dict, Tuple
import sys
import importlib
import pysqlite3
sys.modules["sqlite3"] = pysqlite3
importlib.reload(pysqlite3)

import chromadb
from sentence_transformers import SentenceTransformer
import networkx as nx
import pickle
import os
import logging
import numpy as np
import re

logging.basicConfig(level=logging.INFO)

class HybridStorage:
    def __init__(self):
        self.chroma_client = chromadb.PersistentClient(path="./chroma_db")
        self.collection = self.chroma_client.get_or_create_collection("shadow_docs")
        self.embedding_model = None
        self.graph = nx.Graph()
        self.graph_file = "entity_graph.pkl"
        self.initialized = False

    def load_embedding_model(self):
        if self.embedding_model is None:
            logging.info("Loading SentenceTransformer for storage")
            self.embedding_model = SentenceTransformer("all-MiniLM-L6-v2", trust_remote_code=False)

    def store_chunks(self, chunks: List[Dict]):
        if not chunks:
            logging.error("No chunks provided to store")
            raise ValueError("Chunks list is empty")

        cache_valid = (
            self.initialized and
            os.path.exists(self.graph_file) and
            self.collection.count() >= len(chunks)
        )
        
        if cache_valid:
            try:
                with open(self.graph_file, "rb") as f:
                    self.graph = pickle.load(f)
                expected_nodes = len(chunks)
                entity_nodes = sum(1 for n, d in self.graph.nodes(data=True) if d.get("type") == "entity")
                if self.graph.number_of_nodes() < expected_nodes or entity_nodes < len(chunks) // 2:
                    logging.warning(f"Graph has {self.graph.number_of_nodes()} nodes, {entity_nodes} entities, expected at least {expected_nodes} nodes with ~{len(chunks)//2} entities, rebuilding")
                    cache_valid = False
                else:
                    logging.info("Using existing ChromaDB index and graph")
                    return
            except Exception as e:
                logging.error(f"Failed to load entity_graph.pkl: {str(e)}")
                cache_valid = False

        self.load_embedding_model()
        doc_id = "secret_info_manual"
        contents = []
        metadatas = []
        ids = []

        for chunk in chunks:
            content = chunk["content"]
            entities = chunk["entities"]
            chunk_id = chunk["chunk_id"]

            clearance = None
            clearance_match = re.search(r'clearance level:\s*(\d+)', content, re.IGNORECASE)
            if clearance_match:
                clearance = int(clearance_match.group(1))
            
            contents.append(content)
            metadatas.append({
                "doc_id": doc_id,
                "clearance": clearance if clearance is not None else -1,
                "entities": ",".join([e for e in entities if e]),
                "chunk_id": chunk_id
            })
            ids.append(chunk_id)

        try:
            embeddings = self.embedding_model.encode(contents, convert_to_tensor=False, show_progress_bar=False)
            embeddings_list = []
            for i, emb in enumerate(embeddings):
                if isinstance(emb, np.ndarray):
                    embeddings_list.append(emb.tolist())
                elif isinstance(emb, list) and all(isinstance(x, (int, float)) for x in emb):
                    embeddings_list.append(emb)
                else:
                    logging.error(f"Invalid embedding at index {i}: {type(emb)}")
                    raise ValueError(f"Embedding at index {i} is not a valid array or list")
                if not all(isinstance(x, (int, float)) for x in embeddings_list[-1]):
                    logging.error(f"Invalid values in embedding at index {i}: {embeddings_list[-1]}")
                    raise ValueError(f"Embedding at index {i} contains non-numeric values")

            logging.info(f"Upserting {len(chunks)} chunks to ChromaDB")
            self.collection.upsert(
                documents=contents,
                embeddings=embeddings_list,
                metadatas=metadatas,
                ids=ids
            )
        except Exception as e:
            logging.error(f"Failed to upsert to ChromaDB: {str(e)}")
            raise

        self.graph.clear()
        entity_count = 0
        chunk_count = 0
        for chunk in chunks:
            chunk_id = chunk["chunk_id"]
            entities = [e.strip() for e in chunk["entities"] if e.strip() and len(e) > 2]
            if not entities:
                logging.warning(f"No valid entities for chunk {chunk_id}: {chunk['content'][:50]}...")
            self.graph.add_node(chunk_id, type="chunk", content=chunk["content"])
            chunk_count += 1
            for entity in entities:
                self.graph.add_node(entity, type="entity")
                self.graph.add_edge(chunk_id, entity, relation="contains")
                entity_count += 1

        try:
            with open(self.graph_file, "wb") as f:
                pickle.dump(self.graph, f)
            logging.info(f"Stored {chunk_count} chunks and built graph with {self.graph.number_of_nodes()} nodes, {entity_count} entities")
        except Exception as e:
            logging.error(f"Failed to save entity_graph.pkl: {str(e)}")
            raise

        if entity_count < len(chunks) // 2:
            logging.warning(f"Low entity count ({entity_count}), expected ~{len(chunks)//2}, graph may be limited")
        if chunk_count == 0:
            logging.error("No chunks stored, graph is empty")
            raise ValueError("No chunks processed")
        self.initialized = True

    def query(self, query_text: str, agent_level: int, n_results: int = 5) -> Tuple[List[Dict], bool]:
        """
        Query ChromaDB and graph, filter by clearance.
        Returns (results, denied_due_to_clearance).
        """
        results = []
        denied_due_to_clearance = False
        
        try:
            query_results = self.collection.query(
                query_texts=[query_text],
                n_results=n_results
            )
            
            for doc, metadata in zip(query_results["documents"][0], query_results["metadatas"][0]):
                clearance = metadata.get("clearance", -1)
                if clearance == -1 or agent_level >= clearance:
                    results.append({
                        "content": doc,
                        "metadata": metadata
                    })
                else:
                    denied_due_to_clearance = True
            
            if not self.graph.nodes:
                logging.warning("Graph is empty, skipping graph search")
        
        except Exception as e:
            logging.error(f"Storage query failed: {str(e)}")
        
        return results, denied_due_to_clearance