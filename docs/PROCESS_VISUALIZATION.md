# Process Visualization — rag-ollama-set-up (end-to-end)



\# Process Visualization — rag-ollama-set-up (end-to-end)



\## 1) Big Picture: Setup → Runtime



```mermaid

flowchart TD

&nbsp; %% ===== SETUP =====

&nbsp; subgraph Setup\[Setup / Installation]

&nbsp;   A\[Install Ollama] --> A2\[Pull models: bge-m3 + gemma3:4b]

&nbsp;   B\[Install PostgreSQL 16] --> C\[Install pgvector into PostgreSQL]

&nbsp;   C --> C1\[Copy vector.dll + vector.control + vector--\*.sql into PGROOT]

&nbsp;   C1 --> C2\[CREATE EXTENSION vector]

&nbsp;   C2 --> D\[Create DB: ragdb]

&nbsp;   D --> E\[Run SQL schema: rag\_setup.sql + rag\_extended.sql]

&nbsp;   F\[Install Python deps: requirements.txt] --> G\[Set env vars: PGHOST/PGPORT/PGUSER/PGDATABASE/PGPASSWORD]

&nbsp; end



&nbsp; %% ===== RUNTIME =====

&nbsp; subgraph Runtime\[Runtime / Usage]

&nbsp;   H\[Ingest documents\\nscripts/ingest.py] --> H1\[Chunk text]

&nbsp;   H1 --> H2\[Embed chunks via Ollama\\n(bge-m3)]

&nbsp;   H2 --> H3\[Insert into rag\_chunks\\n(+ metadata)]

&nbsp;   H3 --> H4\[HNSW index enables fast vector search]



&nbsp;   Q\[Ask question\\nscripts/ask\_rag.py] --> Q1\[Embed question via Ollama\\n(bge-m3)]

&nbsp;   Q1 --> Q2\[Vector search top-k\\nORDER BY embedding <=> qvec]

&nbsp;   Q2 --> GATE{Gate relevance?}

&nbsp;   GATE -- Not relevant --> QNR\[Answer: not enough info\\n(or fallback)]

&nbsp;   GATE -- Relevant --> Q3\[Build prompt with retrieved context]

&nbsp;   Q3 --> Q4\[Generate answer via Ollama\\n(gemma3:4b)]

&nbsp;   Q4 --> LOG\[Log into qa\_log\\n(question, answer, chunk ids, audit fields)]

&nbsp;   QNR --> LOG



&nbsp;   T\[Run test suite\\nscripts/run\_tests.py] --> T1\[Load tests JSONL]

&nbsp;   T1 --> T2\[Execute ask flow for each test]

&nbsp;   T2 --> T3\[Store results\\nrag\_test\_runs + rag\_test\_results]

&nbsp; end



