🧠 Scalable Web-Aware RAG Engine
🚀 Overview

This project implements a Retrieval-Augmented Generation (RAG) engine that asynchronously ingests web content and allows users to query that ingested knowledge for grounded, fact-based answers.

The system is designed to be scalable, modular, and responsive, using a Redis-based background queue, FAISS for vector similarity search, and SQLite for metadata management.

🏗️ Architecture Overview
                ┌──────────────────────┐
                │   User / Client App   │
                └─────────┬─────────────┘
                          │
          ┌───────────────┴────────────────┐
          │          FastAPI Server         │
          │  (Ingestion & Query Endpoints)  │
          └───────────────┬────────────────┘
                          │
          ┌───────────────┼───────────────────┐
          │               │                   │
  ┌───────▼──────┐  ┌─────▼──────┐     ┌─────▼──────┐
  │   Redis MQ    │  │   SQLite   │     │   FAISS    │
  │ (Job Queue)   │  │ (Metadata) │     │ (Embeddings)│
  └───────────────┘  └────────────┘     └─────────────┘
                          │
                          ▼
                 ┌────────────────────┐
                 │  Background Worker  │
                 │ (Async Ingestion)   │
                 └────────────────────┘

⚙️ Core Components
1. Redis Queue

Acts as a message broker for ingestion jobs.

Allows URL processing to happen asynchronously in a worker process.

Ensures the API remains responsive and non-blocking.

2. SQLite Metadata Store

Tracks ingestion status and metadata.

Contains two main tables:

urls — Tracks URL ingestion lifecycle.

chunks — Stores text chunks extracted from URLs.

Table: urls
Column	Type	Description
id	INTEGER (PK)	Unique ID
url	TEXT	The submitted URL
status	TEXT	pending, processing, completed, or failed
submitted_at	DATETIME	Timestamp when URL was submitted
started_at	DATETIME	When processing began
completed_at	DATETIME	When processing finished
chunk_count	INTEGER	Number of extracted text chunks
error_message	TEXT	Error details if ingestion failed
Table: chunks
Column	Type	Description
id	INTEGER (PK)	Unique ID
url_id	INTEGER (FK)	Reference to urls.id
chunk_index	INTEGER	Chunk number (order)
text	TEXT	Full chunk text
snippet	TEXT	Short preview of the chunk
created_at	DATETIME	Timestamp of creation
3. FAISS Vector Database

Stores embeddings for each chunk of text.

Enables fast semantic similarity search during query time.

Used to retrieve the most relevant text snippets for grounding LLM responses.

🧩 API Endpoints
1. POST /ingest-url

Submit one or more URLs for ingestion.

Request Body:

{
  "urls": [
    "https://example.com/article1",
    "https://example.com/article2"
  ]
}


Response (202 Accepted):

{
  "message": "URLs submitted successfully.",
  "submitted_urls": [
    "https://example.com/article1",
    "https://example.com/article2"
  ]
}


Behavior:

Validates input URLs.

Inserts records into the urls table (status = pending).

Pushes ingestion jobs to Redis for background processing.

Returns immediately with HTTP 202 Accepted.

2. POST /query

Ask questions against the ingested data.

Request Body:

{
  "query": "What are the main points from example.com/article1?"
}


Response:

{
  "answer": "The article discusses...",
  "relevant_chunks": [
    {"snippet": "Main topic of the article..."},
    {"snippet": "Further explanation about..."}
  ]
}


Behavior:

Embeds the input query using the same embedding model as ingestion.

Searches FAISS for top relevant chunks.

Returns a grounded answer along with the supporting snippets.

🧠 Workflow Summary

Client → /ingest-url
→ API validates URLs and enqueues jobs in Redis.

Worker Process

Consumes jobs from Redis.

Fetches web content and cleans it.

Splits text into manageable chunks.

Creates embeddings for each chunk and stores them in FAISS.

Updates status and metadata in SQLite.

Client → /query

Embeds the query.

Retrieves similar chunks from FAISS.

Constructs a grounded, context-aware answer.

💾 Technology Stack
Component	Technology	Reason
Web Framework	FastAPI	High-performance async API framework
Queue	Redis	Lightweight and fast message broker
Vector Store	FAISS	Efficient similarity search for embeddings
Metadata DB	SQLite	Simple and portable relational DB
Background Worker	Python Worker	Handles ingestion asynchronously
LLM / Embedding	OpenAI / SentenceTransformers (configurable)	For embedding and response generation
🧰 Setup Instructions
1. Clone the Repository
git clone https://github.com/yourusername/web-aware-rag-engine.git
cd web-aware-rag-engine

2. Create a Virtual Environment
python -m venv venv
source venv/bin/activate   # For Mac/Linux
venv\Scripts\activate      # For Windows

3. Install Dependencies
pip install -r requirements.txt

4. Configure Environment Variables

Copy the example file and update with your own values:

cp .env.example .env


Example .env.example:

REDIS_URL=redis://localhost:6379
SQLITE_PATH=rag_metadata.db
FAISS_INDEX_PATH=faiss_index.index
EMBEDDING_MODEL=text-embedding-ada-002
OPENAI_API_KEY=your_openai_api_key_here

5. Run Redis

Make sure Redis server is running:

redis-server

6. Start the FastAPI Server
uvicorn main:app --reload

7. Start the Background Worker
python worker.py

🧪 Example Usage
Ingest URLs
curl -X POST http://localhost:8000/ingest-url \
     -H "Content-Type: application/json" \
     -d '{"urls": ["https://example.com/article1"]}'

Query the Knowledge Base
curl -X POST http://localhost:8000/query \
     -H "Content-Type: application/json" \
     -d '{"query": "Summarize example.com/article1"}'

🧩 System Design Justification
Design Choice	Justification
Asynchronous ingestion via Redis	Keeps APIs responsive and scalable.
SQLite metadata store	Lightweight relational DB suitable for local or small-scale deployments.
FAISS for vector search	High-performance similarity search at scale.
FastAPI	Async, type-safe, and modern Python web framework.
Modular pipeline	Easy to extend to other DBs (Postgres, ChromaDB, Qdrant) or message queues (RabbitMQ, Kafka).
🧰 File Structure
├── main.py                # FastAPI app with endpoints
├── worker.py              # Background ingestion worker
├── db.py                  # SQLite schema & helper functions
├── vector_store.py        # FAISS index handling
├── requirements.txt
├── .env.example
├── README.md
└── utils/
    ├── text_cleaner.py
    ├── embedder.py
    └── scraper.py

🎥 Demo Video

📹 Demo: Link to your video here

(5–10 minutes walkthrough: ingestion → background worker → query response)

🛡️ Notes

.env file is not committed to version control.

.env.example provides required variable names for easy setup.

Redis jobs can be monitored or cleared using redis-cli commands.

📜 License

This project is released under the MIT License.