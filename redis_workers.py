import redis
import json
from datetime import datetime
from worker import worker  # import your existing worker(url) function

# Connect to Redis
r = redis.StrictRedis(host='localhost', port=6379, db=0, decode_responses=True)

def process_jobs():
    print("🚀 Worker started, waiting for jobs...")

    while True:
        # Blocking pop from the right of the list
        job = r.brpop("url_jobs", timeout=0)
        if job is None:
            continue

        _, job_json = job
        job_data = json.loads(job_json)
        url = job_data["url"]

        print(f"🛠️ Processing URL: {url}")

        try:
            # Here you call your existing worker pipeline
            FAISS_FILE = "faiss_index.idx"
            EMBED_DIM = 384  # for sentence-transformers/all-MiniLM-L12-v2

            worker_output = worker(FAISS_FILE, EMBED_DIM, url)

            # Update status
            job_data["status"] = "completed"
            job_data["completed_at"] = datetime.utcnow().isoformat()
            print(f"✅ Completed URL: {url}")

        except Exception as e:
            job_data["status"] = "failed"
            job_data["error_message"] = str(e)
            print(f"❌ Failed URL: {url}, Error: {e}")

if __name__ == "__main__":
    process_jobs()
