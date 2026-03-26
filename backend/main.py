from fastapi import FastAPI, HTTPException, Header, Request
from fastapi.middleware.cors import CORSMiddleware
from google.cloud import tasks_v2, firestore
import uuid, json

app = FastAPI()

# --- Configuration ---
API_KEY = "demo123"
PROJECT_ID = "gcp-lab-490622"
QUEUE = "export-queue"
LOCATION = "us-central1"
WORKER_URL = "https://export-worker-374229827468.us-central1.run.app/process"  # worker endpoint
BUCKET_NAME = "demo-export-vadims-12345"

# --- CORS setup ---
origins = [
    "https://frontend-374229827468.us-central1.run.app",
    "http://localhost:3000",  # optional for local testing
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Initialize Firestore and Cloud Tasks ---
db = firestore.Client()
tasks_client = tasks_v2.CloudTasksClient()

# --- API endpoints ---
@app.post("/api/export")
async def export_api(x_api_key: str = Header(...)):
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Unauthorized")

    # Generate a new job ID and mark as pending
    job_id = str(uuid.uuid4())
    db.collection("jobs").document(job_id).set({"status": "pending"})

    # Create Cloud Task to trigger the worker
    parent = tasks_client.queue_path(PROJECT_ID, LOCATION, QUEUE)
    task = {
        "http_request": {
            "http_method": tasks_v2.HttpMethod.POST,
            "url": WORKER_URL,
            "headers": {
                "Content-Type": "application/json",
                "x-api-key": API_KEY  # pass API key to worker
            },
            # ensure JSON body is bytes
            "body": json.dumps({"job_id": job_id, "type": "export"}).encode()
        }
    }
    tasks_client.create_task(request={"parent": parent, "task": task})

    return {"job_id": job_id, "status": "pending"}

# @app.post("/process")
# async def process_task(request: Request, x_api_key: str = Header(...)):
#     # Validate API key
#     if x_api_key != API_KEY:
#         raise HTTPException(status_code=401, detail="Unauthorized")

#     # Parse JSON body
#     try:
#         payload = await request.json()
#     except Exception:
#         raise HTTPException(status_code=400, detail="Invalid JSON payload")

#     job_id = payload.get("job_id")
#     job_type = payload.get("type")

#     if not job_id or not job_type:
#         raise HTTPException(status_code=400, detail="Missing job_id or type")

#     print(f"Worker: processing {job_type} job {job_id}")

#     # Update Firestore job status
#     db.collection("jobs").document(job_id).update({"status": "completed"})

#     return {"status": "ok"}

@app.get("/api/jobs/{job_id}/status")
async def job_status(job_id: str, x_api_key: str = Header(...)):
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Unauthorized")

    doc = db.collection("jobs").document(job_id).get()
    if not doc.exists:
        raise HTTPException(status_code=404, detail="Job not found")

    return doc.to_dict()