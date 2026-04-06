import os
from typing import Dict, Any

from .intent import detect_intent, intent_reply
from .vector_store import query_faq


def answer(message: str) -> Dict[str, Any]:
    intent, confidence = detect_intent(message)
    if intent != "unknown" and confidence >= 0.7:
        return {
            "reply": intent_reply(intent),
            "intent": intent,
            "sources": []
        }

    threshold = float(os.getenv("SIMILARITY_THRESHOLD", "0.45"))
    results = query_faq(message, n_results=1)
    distances = results.get("distances", [[]])[0]
    metadatas = results.get("metadatas", [[]])[0]

    if not distances or distances[0] > threshold:
        return {
            "reply": "I am not sure yet. Could you rephrase or share more details?",
            "intent": "fallback",
            "sources": []
        }

    answer_text = metadatas[0].get("answer", "I can help with bookings and policies.")
    return {
        "reply": answer_text,
        "intent": "rag",
        "sources": metadatas[0].get("tags", [])
    }
