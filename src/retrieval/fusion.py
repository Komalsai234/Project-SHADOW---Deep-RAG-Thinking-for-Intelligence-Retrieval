from typing import List, Dict
from sentence_transformers import CrossEncoder
import logging

logging.basicConfig(level=logging.INFO)

class ResultFusion:
    def __init__(self):
        self.cross_encoder = None

    def load_cross_encoder(self):
        if self.cross_encoder is None:
            logging.info("Loading CrossEncoder for fusion")
            self.cross_encoder = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2", trust_remote_code=False)

    def fuse(self, query: str, result_sets: List[List[Dict]], top_k: int = 5) -> List[Dict]:
        self.load_cross_encoder()
        try:
            combined = []
            seen_content = set()
            for results in result_sets:
                if not results:
                    continue
                for r in results:
                    content = r["content"]
                    if content not in seen_content:
                        combined.append(r)
                        seen_content.add(content)

            if not combined:
                logging.info("No results to fuse")
                return []

            pairs = [[query, r["content"]] for r in combined]
            scores = self.cross_encoder.predict(pairs, show_progress_bar=False)

            for r, score in zip(combined, scores):
                r["score"] = float(score)

            sorted_results = sorted(combined, key=lambda x: x["score"], reverse=True)[:top_k]
            logging.info(f"Fused {len(sorted_results)} results")
            return sorted_results
        except Exception as e:
            logging.error(f"Result fusion failed: {str(e)}")
            return []