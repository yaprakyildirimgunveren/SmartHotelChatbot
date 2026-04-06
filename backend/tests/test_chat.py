from unittest.mock import patch

from app.services.booking_session import clear_sessions
from app.services.chat import answer


def setup_function() -> None:
    clear_sessions()


def test_booking_starts_and_continues_session():
    r1 = answer("rezervasyon yapmak istiyorum", None)
    assert r1["intent"] == "booking"
    assert "şehir" in r1["reply"].lower()
    sid = r1["session_id"]

    r2 = answer("Kapadokya", sid)
    assert r2["intent"] == "booking"
    assert "tarih" in r2["reply"].lower() or "giriş" in r2["reply"].lower()


@patch("app.services.chat.query_faq")
def test_rag_fallback(mock_q):
    mock_q.return_value = {"distances": [[0.99]], "metadatas": [[{"answer": "x", "tags": "a,b"}]]}
    r = answer("asdfghjkl qwerty random", None)
    assert r["intent"] == "fallback"


@patch("app.services.chat.query_faq")
def test_rag_hit(mock_q):
    mock_q.return_value = {"distances": [[0.1]], "metadatas": [[{"answer": "FAQ cevap", "tags": "p1,p2"}]]}
    r = answer("xyz unknown intent text", None)
    assert r["intent"] == "rag"
    assert r["reply"] == "FAQ cevap"
    assert "p1" in r["sources"]
