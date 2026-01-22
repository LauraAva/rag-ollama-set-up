# \# Process Visualization — rag-ollama-set-up (end-to-end)

# 

\## 1) Big Picture: Setup → Runtime

```mermaid

flowchart TD

subgraph Setup["Setup (do this once)"]
  direction TD
  S1["Install Ollama (runs the local AI models)"] --> S2["Download the models:<br/>• bge-m3 (makes embeddings)<br/>• gemma3:4b (writes answers)"]

  S3["Install PostgreSQL 16 (database)"] --> S4["Install pgvector (stores and searches embeddings)"]
  S4 --> S5["Copy pgvector extension files into the PostgreSQL folder<br/>(vector.dll, vector.control, vector--*.sql)"]
  S5 --> S6["Enable pgvector in the database<br/>Run: CREATE EXTENSION vector"]
  S6 --> S7["Create the database<br/>Name: ragdb"]
  S7 --> S8["Create tables and indexes<br/>Run: sql/rag_setup.sql and sql/rag_extended.sql"]

  S9["Install Python packages<br/>Run: pip install -r requirements.txt"] --> S10["Set connection settings (environment variables):<br/>PGHOST, PGPORT, PGUSER, PGDATABASE, PGPASSWORD"]
end

subgraph Ingest["Step 1: Add your documents to the system (ingestion)"]
  direction TD
  I1["Run the ingestion script<br/>scripts/ingest.py"] --> I2["Split documents into smaller parts (chunks)"]
  I2 --> I3["Convert each chunk into a numeric representation (embedding)<br/>using Ollama (bge-m3)"]
  I3 --> I4["Save chunks + embeddings + metadata into the database table<br/>rag_chunks"]
  I4 --> I5["Create a fast search index for embeddings<br/>(so searching is quick)"]
end

subgraph Ask["Step 2: Ask a question (question answering)"]
  direction TD
  A1["Run the question script<br/>scripts/ask_rag.py"] --> A2["Convert the question into an embedding<br/>using Ollama (bge-m3)"]
  A2 --> A3["Search the database for the most similar chunks<br/>(vector similarity search)"]
  A3 --> G{"Did we find enough relevant information?"}
  G -- "No" --> A4["Reply: “I do not have enough information to answer.”<br/>(or use a fallback message)"]
  G -- "Yes" --> A5["Build the final prompt:<br/>question + the retrieved chunks"]
  A5 --> A6["Generate the answer using Ollama (gemma3:4b)"]
  A6 --> L["Save a record in the log table qa_log:<br/>question, answer, and which chunks were used"]
  A4 --> L
end

subgraph Tests["Optional: Run automated tests"]
  direction TD
  T1["Run the test script<br/>scripts/run_tests.py"] --> T2["Load test questions from a JSON Lines file"]
  T2 --> T3["For each test: run the same question answering steps"]
  T3 --> T4["Store test results in database tables:<br/>rag_test_runs and rag_test_results"]
end

Setup --> Ingest --> Ask
Ask --> Tests
```
