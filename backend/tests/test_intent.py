from app.services.intent import detect_intent


def test_detect_booking_tr():
    intent, conf = detect_intent("İstanbul için rezervasyon yapmak istiyorum")
    assert intent == "booking"
    assert conf >= 0.7


def test_detect_cancellation_before_booking():
    intent, _ = detect_intent("rezervasyonu iptal etmek istiyorum")
    assert intent == "cancellation"


def test_detect_pricing():
    intent, conf = detect_intent("What is the price for April?")
    assert intent == "pricing"
    assert conf >= 0.7


def test_detect_amenities_tr():
    intent, conf = detect_intent("havuz olan otel var mı")
    assert intent == "amenities"
    assert conf >= 0.7
