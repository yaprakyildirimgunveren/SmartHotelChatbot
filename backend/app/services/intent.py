from typing import Tuple


def detect_intent(message: str) -> Tuple[str, float]:
    text = message.lower()

    cancel_en = ["cancel", "refund", "cancellation"]
    cancel_tr = ["iptal", "iade", "iptal etmek", "rezervasyonu iptal"]
    if any(word in text for word in cancel_en + cancel_tr):
        return "cancellation", 0.9

    book_en = ["book", "reserve", "reservation", "booking"]
    book_tr = ["rezervasyon", "rezervasyon yap", "oda ayır", "konakla", "otel bul"]
    if any(word in text for word in book_en + book_tr):
        return "booking", 0.82

    price_en = ["price", "cost", "budget", "rate"]
    price_tr = ["fiyat", "ücret", "ücreti", "ne kadar", "tarife"]
    if any(word in text for word in price_en + price_tr):
        return "pricing", 0.72

    amen_en = ["breakfast", "amenities", "pool", "spa", "gym"]
    amen_tr = ["kahvaltı", "kahvalti", "olanak", "havuz", "spa", "spor salonu"]
    if any(word in text for word in amen_en + amen_tr):
        return "amenities", 0.72

    return "unknown", 0.0


def intent_reply(intent: str) -> str:
    if intent == "cancellation":
        return (
            "İptal için rezervasyon referansınızı (PNR) veya e-postanızı paylaşın; "
            "politikayı bir sonraki adımda özetleyebilirim."
        )
    if intent == "booking":
        return ""  # chat katmanı start_booking ile başlatır
    if intent == "pricing":
        return (
            "Fiyat için hedef şehir ve tarih aralığını yazın; "
            "böylece uygun seçenekleri özetleyebilirim."
        )
    if intent == "amenities":
        return (
            "Hangi olanaklar önemli? (ör. kahvaltı, havuz, spa, aile odası) "
            "Yazdığınız kriterlere göre filtreleyebilirim."
        )
    return ""
