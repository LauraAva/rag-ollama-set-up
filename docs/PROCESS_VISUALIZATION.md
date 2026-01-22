# \# Process Visualization — rag-ollama-set-up (end-to-end)

# 

\## 1) Big Picture: Setup → Runtime


```mermaid
flowchart TD

subgraph Setup["Setup (do this once)"]
  direction TD

  S1["Install Ollama (runs the local AI models)"]
  S2["Download the models:<br/>• bge-m3 (creates embeddings)<br/>• gemma3:4b (writes answers)"]
  S1 --> S2

  S3["Install PostgreSQL 16 (database)"]
  S4["Install pgvector (store and search embeddings)"]
  S3 --> S4

  S5["Copy pgvector files into the PostgreSQL folder"]
  S6["Enable pgvector in the database"]
  S4 --> S5 --> S6

  S7["Create the database (ragdb)"]
  S8["Create tables and indexes"]
  S6 --> S7 --> S8

  S9["Install Python packages"]
  S10["Set database connection settings"]
  S9 --> S10
end

subgraph Ingest["Step 1: Add documents"]
  direction TD

  I1["Run the ingestion script"]
  I2["Split documents into smaller parts"]
  I3["Create an embedding for each part"]
  I4["Save everything into the database"]
  I5["Create a fast search index"]

  I1 --> I2 --> I3 --> I4 --> I5
end

subgraph Ask["Step 2: Ask a question"]
  direction TD

  A1["Run the question script"]
  A2["Create an embedding for the question"]
  A3["Search the database for similar text"]
  A4["Build a prompt with the found text"]
  A5["Generate the answer"]
  A6["Save the question and answer"]

  A1 --> A2 --> A3 --> A4 --> A5 --> A6
end

Setup --> Ingest --> Ask
```
