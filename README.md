## Smart Hotel Chatbot

Simple NLP-powered hotel reservation assistant with intent routing and FAQ retrieval.

### Features
- Intent detection (booking, cancellation, amenities, pricing)
- FAQ retrieval with embeddings (Chroma + Sentence Transformers)
- Simple web chat UI

### Local run
```
cd backend
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8001
```

Open:
- http://localhost:8001
- http://localhost:8001/health

### Docker
```
docker build -t smart-hotel-chatbot ./backend
docker run -p 8001:8001 smart-hotel-chatbot
```

### Environment
Copy `.env.example` to `.env` and customize:
- `MODEL_NAME`
- `SIMILARITY_THRESHOLD`
- `CHROMA_PATH`
