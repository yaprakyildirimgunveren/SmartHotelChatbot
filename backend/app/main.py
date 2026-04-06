import json
from pathlib import Path
from typing import List

from fastapi import FastAPI
from pydantic import BaseModel

from .services.chat import answer
from .services.vector_store import ensure_seeded

app = FastAPI(title="Smart Hotel Chatbot", version="0.2.0")


class ChatRequest(BaseModel):
    message: str
    session_id: str | None = None


class ChatResponse(BaseModel):
    reply: str
    intent: str
    sources: List[str]
    session_id: str


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
    result = answer(request.message, request.session_id)
    return ChatResponse(**result)


@app.get("/")
def index():
    html = """
<!doctype html>
<html lang="tr">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Smart Hotel Chatbot</title>
  <style>
    body { font-family: Arial, Helvetica, sans-serif; background: #0b1020; color: #f4f6fb;
           padding: 24px; margin: 0; }
    .card { background: #121a33; padding: 20px; border-radius: 12px; max-width: 680px;
            margin: 0 auto; }
    input, button { padding: 10px 14px; border-radius: 8px; border: 1px solid #2a3558;
                    font-size: 15px; }
    input { flex: 1; background: #0b1020; color: #f4f6fb; }
    button { background: #6671ff; color: #fff; cursor: pointer; border: none; }
    button:disabled { opacity: 0.5; cursor: not-allowed; }
    .row { display: flex; gap: 10px; margin-top: 12px; align-items: stretch; }
    #history { margin-top: 16px; max-height: 360px; overflow-y: auto; }
    .bubble { margin-top: 10px; padding: 12px; border-radius: 8px; }
    .bubble.user { background: #1a2548; border-left: 3px solid #6671ff; }
    .bubble.bot { background: #0b1020; border-left: 3px solid #4ade80; white-space: pre-wrap; }
    .label { color: #8aa2ff; font-size: 12px; margin-bottom: 6px; }
    .hint { color: #9ca3c7; font-size: 13px; margin-top: 8px; }
  </style>
</head>
<body>
  <div class="card">
    <h2>Smart Hotel Chatbot</h2>
    <p>Rezervasyon, iptal, fiyat veya otel politikaları için yazın. Oturum bu tarayıcıda saklanır.</p>
    <div class="row">
      <input id="message" placeholder="Mesajınız..." autocomplete="off" />
      <button id="sendBtn" onclick="send()">Gönder</button>
    </div>
    <p class="hint" id="status"></p>
    <div id="history"></div>
  </div>
  <script>
    const KEY = 'smart_hotel_session_id';

    function getSessionId() {
      let id = localStorage.getItem(KEY);
      if (!id) {
        id = crypto.randomUUID();
        localStorage.setItem(KEY, id);
      }
      return id;
    }

    document.getElementById('message').addEventListener('keydown', (e) => {
      if (e.key === 'Enter') send();
    });

    async function send() {
      const input = document.getElementById('message');
      const message = input.value.trim();
      if (!message) return;

      const btn = document.getElementById('sendBtn');
      const status = document.getElementById('status');
      const history = document.getElementById('history');

      btn.disabled = true;
      status.textContent = 'Gönderiliyor…';

      appendBubble('user', message);
      input.value = '';

      try {
        const response = await fetch('/chat', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ message, session_id: getSessionId() })
        });
        const data = await response.json();
        if (data.session_id) {
          localStorage.setItem(KEY, data.session_id);
        }
        const src = (data.sources && data.sources.length)
          ? '<div class="label">Kaynak etiketleri: ' + data.sources.join(', ') + '</div>'
          : '';
        appendBubble('bot', '<div class="label">Yanıt (' + data.intent + ')</div>' + src + escapeHtml(data.reply));
      } catch (err) {
        appendBubble('bot', '<div class="label">Hata</div>Bağlantı kurulamadı.');
      } finally {
        btn.disabled = false;
        status.textContent = '';
      }
    }

    function escapeHtml(s) {
      const d = document.createElement('div');
      d.textContent = s;
      return d.innerHTML;
    }

    function appendBubble(kind, html) {
      const div = document.createElement('div');
      div.className = 'bubble ' + kind;
      div.innerHTML = kind === 'user' ? escapeHtml(html) : html;
      document.getElementById('history').appendChild(div);
      div.scrollIntoView({ behavior: 'smooth', block: 'end' });
    }
  </script>
</body>
</html>
"""
    return html
