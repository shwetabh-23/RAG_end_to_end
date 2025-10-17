import redis
import json
from datetime import datetime

# Connect to Redis
r = redis.StrictRedis(host='localhost', port=6379, db=0, decode_responses=True)

def enqueue_url(url: str):
    """
    Push a new URL job to Redis with status 'pending'.
    """
    job = {
        "url": url,
        "status": "pending",
        "submitted_at": datetime.utcnow().isoformat()
    }
    job_json = json.dumps(job)

    # Add job to the head of the list
    r.lpush("url_jobs", job_json)
    print(f"✅ Enqueued job: {url}")

if __name__ == "__main__":
    # Example URLs
    urls = [
        "https://medium.com/@explorer_shwetabh/deepfake-detection-part-1-understanding-dual-attention-vision-transformers-fac7812f1243",
        "https://medium.com/@explorer_shwetabh/deepfake-detection-part-2-understanding-lora-based-moe-adapter-architecture-813acbf9b345", 
        "https://medium.com/@explorer_shwetabh/understanding-multimodal-large-language-models-mllms-7194e8a373b3", 
        "https://medium.com/@explorer_shwetabh/multi-agentic-rag-system-for-jamming-sessions-d4d592db35aa" , 
        "https://medium.com/@explorer_shwetabh/trying-to-learn-what-they-see-part-1-2a3ff94b58de"
       
    ]

    for url in urls:
        enqueue_url(url)
