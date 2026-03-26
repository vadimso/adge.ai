from fastapi import FastAPI, HTTPException, Header, Request
from google.cloud import firestore
import uvicorn
import json

app = FastAPI()

# ✅ API key for auth
API_KEY = "demo123"

# ✅ Firestore client
db = firestore.Client()

@app.post("/process")
async def process_task(request: Request):
    headers = request.headers
    x_api_key = headers.get("X-API-KEY") or headers.get("x-api-key")
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Unauthorized")

    # Parse JSON body
    payload = await request.json()
    job_id = payload.get("job_id")
    job_type = payload.get("type")

    if not job_id or not job_type:
        raise HTTPException(status_code=400, detail="Missing job_id or type")

    print(f"Worker: processing {job_type} job {job_id}")

    # Update Firestore
    db.collection("jobs").document(job_id).update({"status": "completed"})

    return {"status": "ok"}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)