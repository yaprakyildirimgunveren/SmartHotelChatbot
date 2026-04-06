import os
from typing import Any, Dict

from .booking_session import (
    abort_keywords,
    booking_reply,
    get_or_create_session,
    reset_session,
    start_booking,
)
from .intent import detect_intent, intent_reply
from .vector_store import query_faq


def _normalize_sources(raw: Any) -> list[str]:
    if raw is None:
        return []
    if isinstance(raw, list):
        return [str(x) for x in raw if x]
    if isinstance(raw, str):
        return [t.strip() for t in raw.split(",") if t.strip()]
    return []


def answer(message: str, session_id: str | None) -> Dict[str, Any]:
    sid, state = get_or_create_session(session_id)

    if abort_keywords(message) and state.mode == "booking":
        reset_session(state)
        return {
            "reply": "Rezervasyon akışı iptal edildi. Başka bir konuda yardımcı olabilirim.",
            "intent": "aborted",
            "sources": [],
            "session_id": sid,
        }

    if state.mode == "booking":
        text = booking_reply(state, message)
        return {
            "reply": text,
            "intent": "booking",
            "sources": [],
            "session_id": sid,
        }

    intent, confidence = detect_intent(message)
    if intent == "booking" and confidence >= 0.7:
        first = start_booking(state)
        return {
            "reply": first,
            "intent": "booking",
            "sources": [],
            "session_id": sid,
        }

    if intent != "unknown" and confidence >= 0.7:
        reply = intent_reply(intent)
        return {
            "reply": reply,
            "intent": intent,
            "sources": [],
            "session_id": sid,
        }

    threshold = float(os.getenv("SIMILARITY_THRESHOLD", "0.45"))
    results = query_faq(message, n_results=1)
    distances = results.get("distances", [[]])[0]
    metadatas = results.get("metadatas", [[]])[0]

    if not distances or distances[0] > threshold:
        return {
            "reply": (
                "Şu an net bir yanıt üretemedim. "
                "Rezervasyon, iptal veya otel politikası için cümlenizi biraz açar mısınız?"
            ),
            "intent": "fallback",
            "sources": [],
            "session_id": sid,
        }

    meta = metadatas[0] if metadatas else {}
    answer_text = meta.get("answer", "Rezervasyon ve politikalar konusunda yardımcı olabilirim.")
    tags = _normalize_sources(meta.get("tags"))
    return {
        "reply": answer_text,
        "intent": "rag",
        "sources": tags,
        "session_id": sid,
    }
