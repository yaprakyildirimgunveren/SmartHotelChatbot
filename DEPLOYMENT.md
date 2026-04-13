# Deployment Quickstart

This guide explains how to deploy `SmartHotelChatbot` quickly on common platforms.

## 1) App settings

- **App root:** `backend`
- **Start command:** `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- **Health check path:** `/health`

> If your platform does not provide `$PORT`, use `8001`.

## 2) Required environment variables

- `MODEL_NAME` (example: `all-MiniLM-L6-v2`)
- `SIMILARITY_THRESHOLD` (example: `0.45`)
- `CHROMA_PATH` (example: `/tmp/chroma_db` or mounted volume path)

Optional:
- `PYTHONUNBUFFERED=1`

## 3) Render (Web Service)

1. New Web Service -> connect this GitHub repo.
2. Set **Root Directory** to `backend`.
3. Build command:
   - `pip install -r requirements.txt`
4. Start command:
   - `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
5. Add env vars from section 2.
6. Set Health Check Path to `/health`.

## 4) Railway

1. New Project -> Deploy from GitHub.
2. Set service root to `backend`.
3. Railway auto-detects Python; ensure start command is:
   - `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
4. Add env vars from section 2.
5. Verify `/health` after first deploy.

## 5) Google Cloud Run

1. Build image:
   - `docker build -t gcr.io/<PROJECT_ID>/smart-hotel-chatbot ./backend`
2. Push image:
   - `docker push gcr.io/<PROJECT_ID>/smart-hotel-chatbot`
3. Deploy:
   - `gcloud run deploy smart-hotel-chatbot --image gcr.io/<PROJECT_ID>/smart-hotel-chatbot --platform managed --allow-unauthenticated --region <REGION>`
4. Set env vars from section 2 in Cloud Run service settings.
5. Confirm `/health`.

## 6) Persistence note for Chroma

`CHROMA_PATH` points to local disk. On platforms with ephemeral filesystems, FAQ vectors can be lost on restart/redeploy.

Options:
- Accept reseeding on startup for demo usage.
- Use mounted persistent disk/volume where available.
- Replace local Chroma persistence with managed vector DB for production.

## 7) Post-deploy checklist

- `GET /health` returns `{"status":"ok"}`
- Open `/` and send a test message
- Booking flow works across messages with returned `session_id`
- Check logs for model download or startup errors
