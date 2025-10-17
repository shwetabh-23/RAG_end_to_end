# 🧠 Scalable Web-Aware RAG Engine

This project implements a **Retrieval-Augmented Generation (RAG) engine** that asynchronously ingests web content and allows users to query that ingested knowledge for grounded, fact-based answers.

---

## 🚀 Overview

- **Ingestion API** → Submits one or more URLs for background processing.  
- **Query API** → Allows querying against ingested content.  
- **Redis** → Used as a message queue for async ingestion.  
- **SQLite** → Stores metadata (URLs and text chunks).  
- **FAISS** → Stores and retrieves embeddings for semantic similarity search.

---

## ⚙️ Tech Stack

| Component | Technology |
|------------|-------------|
| Framework | FastAPI |
| Queue | Redis |
| Vector DB | FAISS |
| Metadata DB | SQLite |
| Language | Python 3.x |

---

## 🧩 Database Schema

### Table: `urls`
| Column | Description |
|--------|--------------|
| id | Primary key |
| url | Submitted URL |
| status | `pending` / `processing` / `completed` / `failed` |
| submitted_at | Submission timestamp |
| started_at | Processing start time |
| completed_at | Processing end time |
| chunk_count | Number of extracted chunks |
| error_message | Error details (if any) |

### Table: `chunks`
| Column | Description |
|--------|--------------|
| id | Primary key |
| url_id | Foreign key to `urls.id` |
| chunk_index | Order of chunk |
| text | Chunk text |
| snippet | Short preview |
| created_at | Creation timestamp |

---

## 🧠 API Endpoints

### `POST /ingest-url`
Submit one or more URLs for ingestion.

🧩 Workflow

POST /ingest-url → Adds URLs to Redis queue.

Worker → Fetches content, cleans it, chunks it, embeds it, and stores it in FAISS and SQLite.

POST /query → Embeds the query, retrieves relevant chunks, and generates a grounded answer.

🧰 Setup
# 1. Clone the repository
git clone https://github.com/shwetabh-23/RAG_end_to_end.git
cd RAG_end_to_end

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate   # or venv\Scripts\activate on Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Create environment file
cp .env.example .env