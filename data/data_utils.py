import sqlite3
from datetime import datetime
import pandas as pd

from text_utils import chunk_text
from get_data import extract_text_from_html, fetch_html

# Connect to (or create) database file
conn = sqlite3.connect("rag_metadata.db")

def create_tables() : 
    # Create tables
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS urls (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        url TEXT UNIQUE NOT NULL,
        status TEXT NOT NULL DEFAULT 'pending',
        submitted_at TEXT NOT NULL,
        started_at TEXT,
        completed_at TEXT,
        chunk_count INTEGER DEFAULT 0,
        error_message TEXT
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS chunks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        url_id INTEGER NOT NULL,
        chunk_index INTEGER NOT NULL,
        text TEXT NOT NULL,
        snippet TEXT,
        created_at TEXT NOT NULL
    );
    """)

    conn.commit()
    print("Database and tables created successfully.")
    

def insert_chunks(url, chunks):
    """
    Insert chunks for a given URL into SQLite and return FAISS IDs.

    Args:
        conn: sqlite3 connection object
        url (str): URL of the document
        chunks (List[str]): List of chunk texts

    Returns:
        List[int]: List of FAISS IDs (chunks.id) corresponding to inserted chunks
    """
    cursor = conn.cursor()

    # Get URL ID
    cursor.execute("SELECT id FROM urls WHERE url=?", (url,))
    result = cursor.fetchone()
    if not result:
        raise ValueError(f"URL {url} not found in urls table.")
    url_id = result[0]

    faiss_ids = []

    # Insert chunks
    for idx, chunk_text in enumerate(chunks):
        if not isinstance(chunk_text, str) or chunk_text.strip() == "":
            print(f"⚠️ Skipping invalid chunk: {chunk_text}")
            continue

        snippet = chunk_text[:100]  # first 100 characters
        created_at = datetime.utcnow().isoformat()
        cursor.execute("""
            INSERT INTO chunks (url_id, chunk_index, text, snippet, created_at)
            VALUES (?, ?, ?, ?, ?)
        """, (url_id, idx, chunk_text, snippet, created_at))

        # Get the auto-assigned ID as FAISS ID
        faiss_ids.append(cursor.lastrowid)

    # Update URL chunk count
    cursor.execute("UPDATE urls SET chunk_count=? WHERE id=?", (len(chunks), url_id))

    conn.commit()
    return faiss_ids

def insert_urls(url):
    """
    Insert a new URL into the urls table.

    Args:
        conn: sqlite3 connection object
        url (str): The URL to insert

    Returns:
        int: The auto-generated ID of the inserted URL
    """
    cursor = conn.cursor()
    submitted_at = datetime.utcnow().isoformat()

    try:
        cursor.execute("""
            INSERT INTO urls (url, submitted_at)
            VALUES (?, ?)
        """, (url, submitted_at))
        conn.commit()
        url_id = cursor.lastrowid
        return url_id

    except sqlite3.IntegrityError:
        # URL already exists, fetch its ID
        cursor.execute("SELECT id FROM urls WHERE url=?", (url,))
        url_id = cursor.fetchone()[0]
        return url_id
    
def load_db_as_pandas() : 
    urls_df = pd.read_sql_query("SELECT * FROM urls", conn)
    chunks_df = pd.read_sql_query("SELECT * FROM chunks", conn)
  
    return urls_df, chunks_df

def drop_tables():
    """Delete all tables (urls and chunks) from the SQLite database."""
    
    cursor = conn.cursor()

    # Drop tables if they exist
    cursor.execute("DROP TABLE IF EXISTS chunks;")
    cursor.execute("DROP TABLE IF EXISTS urls;")

    conn.commit()
    print("✅ Tables 'urls' and 'chunks' dropped successfully.")

def update_url_status(url, status, chunk_count=None, error_message=None):
    """
    Update the status, timestamps, and metadata of a given URL in the 'urls' table.
    """
    cursor = conn.cursor()

    timestamp = datetime.utcnow().isoformat()

    if status == "in_progress":
        cursor.execute("""
            UPDATE urls
            SET status=?, started_at=?
            WHERE url=?;
        """, (status, timestamp, url))

    elif status == "completed":
        cursor.execute("""
            UPDATE urls
            SET status=?, completed_at=?, chunk_count=?
            WHERE url=?;
        """, (status, timestamp, chunk_count, url))

    elif status == "failed":
        cursor.execute("""
            UPDATE urls
            SET status=?, completed_at=?, error_message=?
            WHERE url=?;
        """, (status, timestamp, error_message, url))

    else:
        cursor.execute("""
            UPDATE urls
            SET status=?
            WHERE url=?;
        """, (status, url))

    conn.commit()

def get_chunks_from_db(faiss_ids):
    """
    Fetch chunks from the SQLite 'chunks' table based on FAISS IDs.

    Args:
        conn: sqlite3.Connection object
        faiss_ids: list of FAISS IDs (integers or strings)

    Returns:
        List of dicts: [{"chunk_index": int, "text": str, "snippet": str, "faiss_id": str}, ...]
    """

    if not faiss_ids:
        return []

    # Build SQL placeholders dynamically
    placeholders = ",".join("?" for _ in faiss_ids)
    query = f"""
        SELECT id, chunk_index, text, snippet
        FROM chunks
        WHERE id IN ({placeholders})
    """

    conn = conn = sqlite3.connect("rag_metadata.db", check_same_thread=False)  # 👈 IMPORTANT FIX
    cursor = conn.cursor()
    cursor.execute(query, tuple(faiss_ids))
    rows = cursor.fetchall()

    # Convert to list of dictionaries
    chunks = [
        {
            "faiss_id": row[0],
            "chunk_index": row[1],
            "text": row[2],
            "snippet": row[3]
        }
        for row in rows
    ]

    # Optional: sort by chunk_index if you want them in original order
    chunks.sort(key=lambda x: x["chunk_index"])

    return chunks

if __name__ == '__main__' : 

    drop_tables()
    create_tables()

    # url = "https://medium.com/@explorer_shwetabh/deepfake-detection-part-2-understanding-lora-based-moe-adapter-architecture-813acbf9b345"
    # url_2 = "https://medium.com/@explorer_shwetabh/deepfake-detection-part-1-understanding-dual-attention-vision-transformers-fac7812f1243"
    # html = fetch_html(url_2)
    # if html:
    #     content = extract_text_from_html(html)
    #     # print(content)  # print first 500 characters

    # chunks = chunk_text(content, chunk_size=1000, chunk_overlap=100)

    # insert_urls(conn, url_2)
    # insert_chunks(conn, url_2, chunks)
    # urls, chunks = load_db_as_pandas(conn)
    breakpoint()