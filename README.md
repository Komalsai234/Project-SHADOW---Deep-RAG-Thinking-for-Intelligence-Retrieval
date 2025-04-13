# Project SHADOW - RAW Intelligence System

**Project SHADOW** is a secure, modular intelligence query system for the **RAW Agents’ Query Response Framework**. It enables authorized agents (clearance levels 1, 2, 3, 4, 5, 7, 9) to access classified information via a sophisticated pipeline of LLM-based query classification, rule-based matching, hybrid retrieval, and secure response generation. A simple, attractive Streamlit UI allows agents to submit queries and receive clearance-aware responses, with query types automatically classified using Groq’s LLM. The system integrates vector and graph-based retrieval, robust security protocols, and audit logging for accuracy, confidentiality, and traceability.

## Table of Contents
- [Overview](#overview)
- [Features](#features)
- [Architecture](#architecture)
- [Methodology](#methodology)
- [Workflow](#workflow)
- [File Structure](#file-structure)
- [Dependencies](#dependencies)

## Overview
**Project SHADOW** is a covert platform for RAW agents to retrieve operational protocols, security verifications, and strategic data. It processes queries like “What is the protocol for emergency extraction?” or “Facility X-17 status” by:
- Automatically classifying query types (e.g., `basic_operational`, `advanced_covert`) using `LLMArbitrator`.
- Matching queries against predefined rules with optimized keyword techniques.
- Retrieving data via hybrid vector (ChromaDB) and graph (NetworkX) search.
- Generating LLM-enhanced responses, restricted by clearance levels.
- Logging interactions for security and auditability.
- Displaying results in a clean Streamlit UI.

The system ensures security, scalability, and ease of use, delivering authorized information through a professional interface.

## Features
- **Query Classification**:
  - `llm_arbitration.py` uses Groq’s `llama3-70b-8192` to classify queries into categories (e.g., `basic_operational`, `cyber_intel`).
  - Fallback to `universal` for ambiguous or failed classifications.
- **Rule-Based Matching**:
  - `rule_engine.py` employs set-based keyword matching (75% threshold for >2 keywords, full match for ≤2).
  - Rules like “emergency extraction protocol” (level 1) or “facility x-17 after 2 AM UTC” (any level).
  - Universal rules (e.g., “omega echo”) apply broadly.
- **Hybrid Retrieval**:
  - `vector_search.py`: Semantic search via ChromaDB (`all-MiniLM-L6-v2`).
  - `graph_search.py`: Entity-based search using NetworkX (e.g., “Ghost-Step Algorithm”).
  - `fusion.py`: Combines results for optimal relevance.
- **Response Generation**:
  - `llm_generator.py`: Formats responses with LLM, includes greetings (e.g., “Salute, Shadow Cadet.”).
  - Handles “Access Denied” for clearance violations.
- **Security**:
  - `access_control.py`: Enforces clearance (e.g., denies level 3 for clearance 7).
  - `audit_ledger.py`: Logs queries and outcomes.
  - `protocol_plugins.py`: Extensible security (e.g., encryption, sanitization).
- **Streamlit UI**:
  - Light gray background, teal accents, Roboto font.
  - Inputs: agent level, query text (query type auto-classified).
  - Scrollable response area.
- **Performance**:
  - Precomputes rules, embeddings, and graph for ~1s queries post-initialization.
  - Caches `PipelineOrchestrator` with `@st.cache_resource`.

## Architecture
The system is modular:
- **UI Layer** (`streamlit_app.py`):
  - Streamlit interface for query input and response display.
  - Inputs: agent level, query text.
  - Outputs: classified query type, response, or errors.
- **Orchestration Layer** (`orchestrator.py`):
  - `PipelineOrchestrator` coordinates classification, rules, retrieval, security, and generation.
  - Initializes ingestion and indexing.
- **Classification Layer** (`llm_arbitration.py`):
  - `LLMArbitrator` classifies queries using Groq’s LLM.
- **Response Layer** (`rule_engine.py`, `llm_generator.py`):
  - `rule_engine.py`: Matches queries against `rules.json`.
  - `llm_generator.py`: Generates responses with LLM.
- **Retrieval Layer** (`fusion.py`, `graph_search.py`, `vector_search.py`):
  - `vector_search.py`: ChromaDB semantic search.
  - `graph_search.py`: NetworkX entity traversal.
  - `fusion.py`: Merges results by relevance and clearance.
- **Security Layer** (`access_control.py`, `audit_ledger.py`, `protocol_plugins.py`):
  - `access_control.py`: Clearance filtering.
  - `audit_ledger.py`: Query logging.
  - `protocol_plugins.py`: Security extensions.
- **Ingestion Layer** (`chunking.py`, `storage.py`):
  - `HierarchicalChunker`: Chunks `secret_info_manual.txt`, extracts entities.
  - `HybridStorage`: Manages ChromaDB and graph.
- **Data**:
  - `rules.json`: Rule conditions and responses.
  - `secret_info_manual.txt`: Classified text with clearance levels.

## Methodology
The system employs a layered approach:
1. **Data Ingestion**:
   - `chunking.py` splits `secret_info_manual.txt` (max 500 chars), extracts entities (e.g., “Ghost-Step Algorithm”).
   - `storage.py` embeds chunks in ChromaDB, builds NetworkX graph.
2. **Query Classification**:
   - `llm_arbitration.py` uses Groq LLM to classify queries (e.g., “emergency extraction” → `basic_operational`).
   - Temperature 0.1 ensures deterministic output; fallback to `universal`.
3. **Rule Processing**:
   - `rule_engine.py` preprocesses `rules.json` into keyword sets (no stop words).
   - Matches queries via set intersection (75% for >2 keywords, full for ≤2).
4. **Retrieval**:
   - `vector_search.py`: Queries ChromaDB for semantic matches.
   - `graph_search.py`: Traverses graph for entity links.
   - `fusion.py`: Ranks combined results, respects clearance.
5. **Security**:
   - `access_control.py` filters by agent level (e.g., denies level 3 for clearance 7).
   - `audit_ledger.py` logs query details.
   - `protocol_plugins.py` applies checks (e.g., sanitization).
6. **Response Generation**:
   - `llm_generator.py` formats responses with LLM, adds greetings.
   - Returns “Access Denied” or “No information” as needed.
7. **Presentation**:
   - `streamlit_app.py` shows query type and response in a clean UI.

## Workflow
1. **User Input**:
   - Agent selects clearance level (1–9) and enters query (e.g., “What is the protocol for emergency extraction?”).
2. **Initialization**:
   - `PipelineOrchestrator` loads `rules.json`, chunks `secret_info_manual.txt`, builds `entity_graph.pkl` and ChromaDB index (first run: 10–30s).
3. **Classification**:
   - `LLMArbitrator` classifies query (e.g., `basic_operational`).
4. **Security Check**:
   - `access_control.py` validates clearance.
   - `protocol_plugins.py` sanitizes input.
5. **Rule Matching**:
   - `rule_engine.py` matches query against rules for classified type and `universal`.
   - Example: “emergency extraction” → Rule 1 (3/3 keywords, level 1).
6. **Retrieval Fallback**:
   - If no rule matches, `fusion.py` coordinates:
     - `vector_search.py`: ChromaDB search.
     - `graph_search.py`: Graph search.
     - Filters via `access_control.py`.
   - Flags `denied_due_to_clearance` if restricted.
7. **Response Generation**:
   - `llm_generator.py` outputs:
     - Rule: e.g., “Salute, Shadow Cadet. Emergency extraction involves…”
     - Retrieval: e.g., “Eyes open, Phantom. Ghost-Step Algorithm enables…”
     - Denial: e.g., “Eyes open, Phantom. Access Denied.”
     - No results: e.g., “Greetings, Agent. No relevant information found.”
8. **Audit Logging**:
   - `audit_ledger.py` records query, type, level, and response.
9. **UI Display**:
   - Streamlit shows query type and response.

## File Structure
```
project-shadow/
├── data/
│   └── secret_info_manual.txt  # Classified text
├── rules/
│   └── rules.json             # Rule definitions
├── src/
│   ├── classification/
│   │   └── llm_arbitration.py # Query type inference
│   ├── ingestion/
│   │   ├── chunking.py        # Text chunking
│   │   └── storage.py         # Data storage
│   ├── pipeline/
│   │   └── orchestrator.py    # Query orchestration
│   ├── response/
│   │   ├── llm_generator.py   # LLM response generation
│   │   └── rule_engine.py     # Keyword matching
│   ├── retrieval/
│   │   ├── fusion.py          # Combines vector/graph results
│   │   ├── graph_search.py    # Entity-based search
│   │   └── vector_search.py   # Semantic search
│   ├── security/
│   │   ├── access_control.py  # Clearance enforcement
│   │   ├── audit_ledger.py    # Query logging
│   │   └── protocol_plugins.py# Security extensions
│   └── ui/
│       └── streamlit_app.py   # Streamlit UI
├── .env                       # GROQ_API_KEY
├── requirements.txt           # Dependencies
├── chroma_db/                 # ChromaDB 
├── entity_graph.pkl           # Graph 
```

## Dependencies

```
streamlit==1.36.0
sentence-transformers==3.0.1
chromadb==0.4.24
groq==0.13.0
python-dotenv==1.0.1
transformers==4.40.0
torch==2.3.0
nltk==3.8.1
rank-bm25==0.2.2
scikit-learn==1.3.0
pyyaml==6.0.1
networkx==3.1
httpx==0.27.2
pipdeptree==2.23.4
numpy==1.26.4
onnxruntime==1.21.0
```