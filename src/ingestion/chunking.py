from typing import List, Dict
import re
import logging

logging.basicConfig(level=logging.INFO)

class HierarchicalChunker:
    def __init__(self, max_chunk_size: int = 500):
        self.max_chunk_size = max_chunk_size

    def extract_entities(self, text: str) -> List[str]:
        text = text.lower()
        patterns = [
            r'\b[A-Z][a-z]*\s[A-Z][a-z]*\b',
            r'\b\w+-\w+\b',
            r'\b[A-Z]+/\w+-\d+\b',
            r'\b(?:shadow|step|safehouse|cipher|seed|regeneration|program|delta-9|k-41|ghost-step|red-flag|omega|protocol|operation|vortex|eclipse|requiem|hollow|void|zeta|phoenix|glass|veil|candle|shop|echo|pattern|circuit|horizon|owl|red|hour|blue|cipher|whispering|gate|iron|vail|black|opal|directive|phase-shift|vault-17|red-mist|x-17|omega-echo|hollow-stone|black-phoenix|ghost-key|opal-directive|iron-vail|omega-circuit|shadow-horizon|red-hour|glass-veil|blue-cipher|whispering-gate|eclipse-protocol|emergency|extraction)\b'  # Keywords
        ]
        entities = []
        for pattern in patterns:
            matches = re.findall(pattern, text)
            entities.extend(matches)

        entities = list(set([e for e in entities if len(e) > 2 and not e.isdigit() and not re.match(r'^[.,:;!?]$', e)]))
        if not entities:
            logging.warning(f"No entities extracted from text: {text[:50]}...")
        else:
            logging.info(f"Extracted entities: {entities}")
        return entities

    def chunk(self, text: str) -> List[Dict]:
        try:
            paragraphs = text.split("\n\n")
            chunks = []
            chunk_id = 0

            for para in paragraphs:
                para = para.strip()
                if not para:
                    continue
                if len(para) <= self.max_chunk_size:
                    entities = self.extract_entities(para)
                    chunks.append({
                        "content": para,
                        "entities": entities,
                        "chunk_id": f"secret_info_manual_{chunk_id}"
                    })
                    chunk_id += 1
                else:
                    sentences = re.split(r'(?<=[.!?])\s+', para)
                    current_chunk = ""
                    current_entities = []
                    for sent in sentences:
                        if len(current_chunk) + len(sent) <= self.max_chunk_size:
                            current_chunk += " " + sent
                            current_entities.extend(self.extract_entities(sent))
                        else:
                            if current_chunk.strip():
                                chunks.append({
                                    "content": current_chunk.strip(),
                                    "entities": list(set(current_entities)),
                                    "chunk_id": f"secret_info_manual_{chunk_id}"
                                })
                                chunk_id += 1
                            current_chunk = sent
                            current_entities = self.extract_entities(sent)
                    if current_chunk.strip():
                        chunks.append({
                            "content": current_chunk.strip(),
                            "entities": list(set(current_entities)),
                            "chunk_id": f"secret_info_manual_{chunk_id}"
                        })
                        chunk_id += 1

            logging.info(f"Created {len(chunks)} chunks")
            if not chunks:
                logging.error("No chunks created from input text")
            return chunks
        except Exception as e:
            logging.error(f"Chunking failed: {str(e)}")
            raise