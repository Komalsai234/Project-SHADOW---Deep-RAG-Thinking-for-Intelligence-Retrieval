from typing import List, Dict
from src.ingestion.chunking import HierarchicalChunker
from src.ingestion.storage import HybridStorage
from src.retrieval.vector_search import VectorSearch
from src.retrieval.graph_search import GraphSearch
from src.retrieval.fusion import ResultFusion
from src.classification.llm_arbitration import LLMArbitrator
from src.security.access_control import AccessControl
from src.security.audit_ledger import AuditLedger
from src.response.rule_engine import RuleEngine
from src.response.llm_generator import LLMGenerator
import logging
import os
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class PipelineOrchestrator:
    def __init__(self):
        groq_api_key = os.getenv("GROQ_API_KEY")
        if not groq_api_key:
            raise ValueError("GROQ_API_KEY is not set in .env file or environment variables")

        logging.info(f"Environment proxies: HTTP_PROXY={os.getenv('HTTP_PROXY')}, HTTPS_PROXY={os.getenv('HTTPS_PROXY')}")

        self.access_control = AccessControl()
        self.audit_ledger = AuditLedger()
        self.rule_engine = RuleEngine()
        self.confidence_threshold = 0.9
        self.chunker = None
        self.storage = None
        self.vector_search = None
        self.graph_search = None
        self.fusion = None
        self.embedding_classifier = None
        self.bert_classifier = None
        self.llm_arbitrator = None
        self.llm_generator = None
        self.initialized = False

    def initialize(self):
        if self.initialized:
            logging.info("Pipeline already initialized")
            return

        logging.info("Initializing heavy components")
        self.chunker = HierarchicalChunker()
        self.storage = HybridStorage()
        self.vector_search = VectorSearch()
        self.graph_search = GraphSearch()
        self.fusion = ResultFusion()
        self.llm_arbitrator = LLMArbitrator()
        self.llm_generator = LLMGenerator()

        try:
            with open("data/secret_info_manual.txt", "r", encoding="utf-8") as f:
                content = f.read()
            chunks = self.chunker.chunk(content)
            self.storage.store_chunks(chunks)

            if not self.storage.graph or self.storage.graph.number_of_nodes() == 0:
                logging.error("Graph initialization failed")
                raise ValueError("Failed to initialize graph in storage")
            self.initialized = True
            logging.info("Initialized pipeline with secret_info_manual.txt.")
        except FileNotFoundError:
            logging.error("secret_info_manual.txt not found in data/")
            raise
        except Exception as e:
            logging.error(f"Initialization failed: {str(e)}")
            raise

    def process_query(self, query: str, agent_level: int) -> str:
        self.audit_ledger.log({"action": "query", "query": query, "agent_level": agent_level})

        if not self.initialized:
            self.initialize()

        try:
            query_type = self.llm_arbitrator.classify(query)

            print(f"Query Type:{query_type}")

            rule_response = self.rule_engine.apply(query, query_type, agent_level)

            print(f"Rule_Response:{rule_response}")

            if rule_response:
                self.audit_ledger.log({"action": "response", "query": query, "response": rule_response})
                return rule_response

            vector_results = self.vector_search.search(query, agent_level)
            graph_results = self.graph_search.search(query, agent_level)
            results = self.fusion.fuse(query, [vector_results, graph_results])

            results, denied_due_to_clearance = self.storage.query(query, agent_level)

            response = self.llm_generator.generate(query, results, agent_level, denied_due_to_clearance)
            
            self.audit_ledger.log({"action": "response", "query": query, "response": response})
            return response
        except Exception as e:
            logging.error(f"Query processing failed: {str(e)}")
            raise