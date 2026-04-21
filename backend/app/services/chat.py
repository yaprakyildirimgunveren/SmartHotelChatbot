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


def _is_unsafe_or_out_of_scope(message: str) -> bool:
    text = message.lower().strip()
    if not text:
        return False

    unsafe_needles = [
        "hack",
        "ddos",
        "malware",
        "bomba",
        "bomb",
        "weapon",
        "silah",
        "yasadışı",
        "illegal",
    ]
    out_of_scope_needles = [
        "stock",
        "crypto",
        "medical",
        "hukuk",
        "law advice",
        "recipe",
        "yemek tarifi",
        "matematik",
        "football",
    ]
    return any(n in text for n in unsafe_needles + out_of_scope_needles)


def _guardrail_reply() -> str:
    return (
        "Bu asistan otel rezervasyon, iptal ve konaklama politikaları için tasarlanmıştır. "
        "Güvenlik veya kapsam dışı taleplerde yardımcı olamam. "
        "İsterseniz şehir, tarih ve misafir sayınızı paylaşarak rezervasyon akışına başlayabiliriz."
    )


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

    if _is_unsafe_or_out_of_scope(message):
        return {
            "reply": _guardrail_reply(),
            "intent": "guardrail",
            "sources": [],
            "recommendations": [],
            "session_id": sid,
        }

    if abort_keywords(message) and state.mode == "booking":
        reset_session(state)
        return {
            "reply": "Rezervasyon akışı iptal edildi. Başka bir konuda yardımcı olabilirim.",
            "intent": "aborted",
            "sources": [],
            "recommendations": [],
            "session_id": sid,
        }

    if state.mode == "booking":
        text, recommendations = booking_reply(state, message)
        return {
            "reply": text,
            "intent": "booking",
            "sources": [],
            "recommendations": recommendations,
            "session_id": sid,
        }

    intent, confidence = detect_intent(message)
    if intent == "booking" and confidence >= 0.7:
        first = start_booking(state)
        return {
            "reply": first,
            "intent": "booking",
            "sources": [],
            "recommendations": [],
            "session_id": sid,
        }

    if intent != "unknown" and confidence >= 0.7:
        reply = intent_reply(intent)
        return {
            "reply": reply,
            "intent": intent,
            "sources": [],
            "recommendations": [],
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
            "recommendations": [],
            "session_id": sid,
        }

    meta = metadatas[0] if metadatas else {}
    answer_text = meta.get("answer", "Rezervasyon ve politikalar konusunda yardımcı olabilirim.")
    tags = _normalize_sources(meta.get("tags"))
    return {
        "reply": answer_text,
        "intent": "rag",
        "sources": tags,
        "recommendations": [],
        "session_id": sid,
    }
