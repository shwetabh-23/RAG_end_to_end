import numpy as np
from datetime import datetime
from get_data import fetch_html, extract_text_from_html
from text_utils import chunk_text
from text_utils import get_embeddings
from faiss_utils import create_faiss_index, add_embeddings_to_index, save_faiss_index, load_faiss_index
from data.data_utils import insert_urls, insert_chunks, update_url_status, load_db_as_pandas   # assume you have these helpers
import faiss
import os

def worker(FAISS_FILE, EMBED_DIM, url):
    """
    Complete RAG ingestion worker:
    1. Fetch and extract text from URL
    2. Split into chunks
    3. Generate embeddings
    4. Store metadata in SQLite
    5. Save vectors in FAISS
    """

    print(f"🚀 Starting worker for URL: {url}")

    try:
        # ----------------------------------------------------------
        # 1. Fetch and Extract Text
        # ----------------------------------------------------------
        html = fetch_html(url)
        if not html:
            raise ValueError("Failed to fetch HTML content.")

        content = extract_text_from_html(html)
        if not content or len(content.strip()) == 0:
            raise ValueError("Extracted content is empty.")

        # ----------------------------------------------------------
        # 2. Chunk the content
        # ----------------------------------------------------------
        chunks = chunk_text(content, chunk_size=1000, chunk_overlap=100)
        if len(chunks) == 0:
            raise ValueError("No valid text chunks generated.")

        print(f"✅ Generated {len(chunks)} chunks")

        # ----------------------------------------------------------
        # 3. Generate embeddings
        # ----------------------------------------------------------
        embeddings = get_embeddings(chunks)
        embeddings = np.array(embeddings).astype('float32')

        print(f"✅ Created embeddings with shape: {embeddings.shape}")

        # ----------------------------------------------------------
        # 4. Insert URL record into DB
        # ----------------------------------------------------------
        url_id = insert_urls(url)
        update_url_status(url, status="processing")

        # ----------------------------------------------------------
        # 5. Assign FAISS IDs and Insert Chunks
        # ----------------------------------------------------------
        # Create FAISS IDs in the form of "urlid_chunknumber"
        # chunk_ids = [int(f"{url_id}{i}") for i in range(len(chunks))]
        faiss_ids = insert_chunks(url, chunks)

        # ----------------------------------------------------------
        # 6. Insert embeddings into FAISS
        # ----------------------------------------------------------
        if os.path.exists(FAISS_FILE):
            print("📂 Existing FAISS index found, loading...")
            index = load_faiss_index(FAISS_FILE, dimension=EMBED_DIM)
            add_embeddings_to_index(index, embeddings, faiss_ids)
        else:
            print("🆕 No existing FAISS index found, creating a new one...")
            index = create_faiss_index(embeddings, faiss_ids)
            print(f"✅ New index created and saved at {FAISS_FILE}")

        print("➕ Adding embeddings to the FAISS index...")
        

        # Save updated index back to disk
        save_faiss_index(index, FAISS_FILE)
        print(f"💾 FAISS index updated and saved at {FAISS_FILE}")

        print(f"Total vectors in index now: {index.ntotal}")

        # ----------------------------------------------------------
        # 7. Finalize
        # ----------------------------------------------------------
        update_url_status(url, status="completed")
        print(f"🎯 URL {url} processed successfully and stored in DB + FAISS.")

        return {
            "url": url,
            "url_id": url_id,
            "chunk_count": len(chunks),
            "faiss_ids": faiss_ids,
        }

    except Exception as e:
        print(f"❌ Error processing {url}: {str(e)}")
        update_url_status(url, status="failed", error_message=str(e))
        return None

if __name__ == '__main__' : 

    url = "https://medium.com/@explorer_shwetabh/deepfake-detection-part-2-understanding-lora-based-moe-adapter-architecture-813acbf9b345"
    
    FAISS_FILE = "faiss_index.idx"
    EMBED_DIM = 384  # for sentence-transformers/all-MiniLM-L12-v2

    worker_output = worker(FAISS_FILE, EMBED_DIM, url)
    urls, chunks = load_db_as_pandas()
    breakpoint()