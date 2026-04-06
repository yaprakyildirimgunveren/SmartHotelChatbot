import json
from pathlib import Path
from typing import List

from fastapi import FastAPI
from pydantic import BaseModel

from .services.chat import answer
from .services.vector_store import ensure_seeded

app = FastAPI(title="Smart Hotel Chatbot", version="0.1.0")


class ChatRequest(BaseModel):
    message: str
    user_id: str | None = None


class ChatResponse(BaseModel):
    reply: str
    intent: str
    sources: List[str]


@app.on_event("startup")
def load_faq() -> None:
    faq_path = Path(__file__).parent / "data" / "faq.json"
    items = json.loads(faq_path.read_text(encoding="utf-8"))
    ensure_seeded(items)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    result = answer(request.message)
    return ChatResponse(**result)


@app.get("/")
def index():
    html = """
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <title>Smart Hotel Chatbot</title>
  <style>
    body { font-family: Arial, Helvetica, sans-serif; background: #0b1020; color: #f4f6fb; padding: 24px; }
    .card { background: #121a33; padding: 20px; border-radius: 12px; max-width: 680px; margin: 0 auto; }
    input, button { padding: 10px; border-radius: 8px; border: 1px solid #2a3558; }
    input { width: 100%; background: #0b1020; color: #f4f6fb; margin-top: 10px; }
    button { margin-top: 12px; background: #6671ff; color: #fff; cursor: pointer; }
    .msg { margin-top: 16px; padding: 12px; background: #0b1020; border-radius: 8px; }
    .label { color: #8aa2ff; font-size: 12px; }
  </style>
</head>
<body>
  <div class="card">
    <h2>Smart Hotel Chatbot</h2>
    <p>Ask about booking, cancellation, amenities, or pricing.</p>
    <input id="message" placeholder="Type your message..." />
    <button onclick="send()">Send</button>
    <div id="response" class="msg"></div>
  </div>
  <script>
    async function send() {
      const message = document.getElementById('message').value;
      const response = await fetch('/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message })
      });
      const data = await response.json();
      document.getElementById('response').innerHTML =
        '<div class="label">Reply (' + data.intent + ')</div>' + data.reply;
    }
  </script>
</body>
</html>
"""
    return html
