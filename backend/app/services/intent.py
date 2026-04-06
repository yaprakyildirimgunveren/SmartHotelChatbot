from typing import Tuple


def detect_intent(message: str) -> Tuple[str, float]:
    text = message.lower()
    if any(word in text for word in ["cancel", "refund", "cancellation"]):
        return "cancellation", 0.9
    if any(word in text for word in ["book", "reserve", "reservation"]):
        return "booking", 0.8
    if any(word in text for word in ["price", "cost", "budget"]):
        return "pricing", 0.7
    if any(word in text for word in ["breakfast", "amenities", "pool", "spa"]):
        return "amenities", 0.7
    return "unknown", 0.0


def intent_reply(intent: str) -> str:
    if intent == "cancellation":
        return "I can help you cancel. Please share your booking reference."
    if intent == "booking":
        return "Great! Tell me the city, dates, and number of guests."
    if intent == "pricing":
        return "Share your target city and dates, and I will estimate pricing."
    if intent == "amenities":
        return "Which amenities are important for you? (breakfast, pool, spa, etc.)"
    return ""
