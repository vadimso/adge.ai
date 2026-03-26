🚀 Scalable Export/Import System (GCP)

        ┌──────────────┐
        │   Frontend   │ (React)
        └──────┬───────┘
               │ HTTP (Start Export)
               ▼
        ┌──────────────┐
        │   Backend    │ (FastAPI - Cloud Run)
        └──────┬───────┘
               │
     ┌─────────┴─────────┐
     │                   │
     ▼                   ▼
┌──────────────┐   ┌──────────────┐
│  Firestore   │   │ Cloud Tasks  │
│ (Job State)  │   │   Queue      │
└──────────────┘   └──────┬───────┘
                          │ HTTP Trigger
                          ▼
                   ┌──────────────┐
                   │    Worker    │ (Cloud Run)
                   └──────┬───────┘
                          │
        ┌─────────────────┼─────────────────┐
        ▼                                   ▼
┌──────────────┐                  ┌──────────────┐
│ Cloud Storage│                  │  Firestore   │
│  (File)      │                  │ (Update Job) │
└──────────────┘                  └──────────────┘

📦 Project Structure
├── backend/
│   ├── main.py
│   ├── requirements.txt
│   └── Dockerfile
├── worker/
│   ├── worker.py
│   ├── requirements.txt
│   └── Dockerfile
└── frontend/
    ├── package.json
    ├── public/
    │   └── index.html
    └── src/
        ├── index.jsx
        └── App.jsx
✅ Prerequisites

GCP Project

Python 3.11+

Node.js 18+

Docker

gcloud CLI

Enable APIs:

gcloud services enable run.googleapis.com
gcloud services enable cloudtasks.googleapis.com
gcloud services enable firestore.googleapis.com
gcloud services enable storage.googleapis.com
1️⃣ Setup GCP Resources
Set project
gcloud config set project gcp-lab-490622
Create Storage Bucket (IMPORTANT: same region)
gsutil mb -l us-central1 gs://demo-export-bucket
Enable Firestore
gcloud firestore databases create --location=us-central1 --type=firestore-native
Mode: Native

Region: us-central1

Create Cloud Tasks queue
gcloud tasks queues create export-queue --location=us-central1
2️⃣ Service Account & Permissions
gcloud iam service-accounts create export-sa

Grant roles:

gcloud projects add-iam-policy-binding gcp-lab-490622 \
  --member="serviceAccount:export-sa@gcp-lab-490622.iam.gserviceaccount.com" \
  --role="roles/datastore.user"

gcloud projects add-iam-policy-binding gcp-lab-490622 \
  --member="serviceAccount:export-sa@gcp-lab-490622.iam.gserviceaccount.com" \
  --role="roles/storage.admin"

gcloud projects add-iam-policy-binding gcp-lab-490622 \
  --member="serviceAccount:export-sa@gcp-lab-490622.iam.gserviceaccount.com" \
  --role="roles/cloudtasks.enqueuer"
3️⃣ Build & Push Docker Images
Authenticate Docker
gcloud auth configure-docker
Backend
cd backend

docker build -t export-api .
docker tag export-api gcr.io/gcp-lab-490622/export-api
docker push gcr.io/gcp-lab-490622/export-api
Worker
cd ../worker

docker build -t export-worker .
docker tag export-worker gcr.io/gcp-lab-490622/export-worker
docker push gcr.io/gcp-lab-490622/export-worker
4️⃣ Deploy Worker (FIRST!)
gcloud run deploy export-worker \
  --image gcr.io/gcp-lab-490622/export-worker \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --service-account export-sa@gcp-lab-490622.iam.gserviceaccount.com \
  --set-env-vars BUCKET_NAME=demo-export-vadims-12345


👉 Copy the Worker URL

5️⃣ Deploy Backend
cd ../backend

gcloud run deploy export-api \
  --image gcr.io/gcp-lab-490622/export-api \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --service-account export-sa@gcp-lab-490622.iam.gserviceaccount.com \
  --set-env-vars \
    WORKER_URL=https://export-worker-374229827468.us-central1.run.app,\
    BUCKET_NAME=demo-export-vadims-12345,\
    PROJECT_ID=gcp-lab-490622,\
    QUEUE_NAME=export-queue,\
    QUEUE_LOCATION=us-central1



6️⃣ Frontend Deployment
cd ../frontend

npm install
npm run build
npx serve -s build

Update API URL:

const API_URL = "https://BACKEND_URL";
7️⃣ Usage Flow

Open frontend

Click Start Export

Backend:

Creates job in Firestore (jobs collection auto-created)

Sends task to Cloud Tasks

Cloud Tasks calls:

POST https://WORKER_URL/process

Worker:

Processes job

Uploads file to Cloud Storage

Updates Firestore

Frontend polls:

GET /api/jobs/{job_id}

Signed URL returned

8️⃣ Load Testing

Install:

pip install aiohttp

Update load_test.py:

API_URL = "https://BACKEND_URL/api/export"

Run:

python load_test_new.ps1
9️⃣ Backend Requirements
✅ Enable CORS (REQUIRED)

In backend/main.py:

from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # restrict in production
    allow_methods=["*"],
    allow_headers=["*"],
)
🔟 Features

Async processing via Cloud Tasks

Scalable workers (Cloud Run auto-scale)

Handles long-running jobs

Secure download via signed URLs

Load testing included
