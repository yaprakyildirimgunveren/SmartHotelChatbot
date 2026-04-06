from app.services.booking_session import (
    UserSession,
    abort_keywords,
    booking_reply,
    clear_sessions,
    get_or_create_session,
    parse_dates,
    parse_guests,
    reset_session,
    start_booking,
)


def setup_function() -> None:
    clear_sessions()


def test_parse_dates_range():
    a, b = parse_dates("2026-04-10 - 2026-04-15")
    assert a == "2026-04-10"
    assert b == "2026-04-15"


def test_parse_guests():
    assert parse_guests("2 yetişkin") == "2"
    assert parse_guests("misafir 3") == "3"


def test_booking_flow_happy_path():
    s = UserSession()
    start_booking(s)
    assert s.mode == "booking"
    r1 = booking_reply(s, " Antalya ")
    assert "tarih" in r1.lower() or "giriş" in r1.lower()
    assert s.step == "dates"
    booking_reply(s, "2026-05-01 - 2026-05-07")
    assert s.step == "guests"
    out = booking_reply(s, "2")
    assert "Özet" in out
    assert s.mode == "idle"


def test_abort_during_booking():
    s = UserSession()
    start_booking(s)
    booking_reply(s, "Izmir")
    assert abort_keywords("iptal")


def test_session_persisted():
    clear_sessions()
    sid1, _ = get_or_create_session(None)
    sid2, st = get_or_create_session(sid1)
    assert sid1 == sid2
    start_booking(st)
    _, st2 = get_or_create_session(sid1)
    assert st2.mode == "booking"


def test_reset_session():
    s = UserSession()
    start_booking(s)
    booking_reply(s, "Bodrum")
    reset_session(s)
    assert s.mode == "idle"
    assert s.city is None
