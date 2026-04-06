from __future__ import annotations

import re
import uuid
from dataclasses import dataclass
from typing import Literal

Mode = Literal["idle", "booking"]
Step = Literal["city", "dates", "guests", "complete"]


@dataclass
class UserSession:
    mode: Mode = "idle"
    city: str | None = None
    check_in: str | None = None
    check_out: str | None = None
    guests: str | None = None
    step: Step = "city"


_sessions: dict[str, UserSession] = {}


def clear_sessions() -> None:
    """Test hook."""
    _sessions.clear()


def get_or_create_session(session_id: str | None) -> tuple[str, UserSession]:
    if session_id and session_id in _sessions:
        return session_id, _sessions[session_id]
    sid = session_id or str(uuid.uuid4())
    if sid not in _sessions:
        _sessions[sid] = UserSession()
    return sid, _sessions[sid]


def abort_keywords(message: str) -> bool:
    text = message.lower()
    needles = (
        "cancel",
        "cancellation",
        "iptal",
        "stop",
        "abort",
        "vazgeç",
        "vazgec",
        "reset",
    )
    return any(n in text for n in needles)


def parse_dates(text: str) -> tuple[str | None, str | None]:
    t = text.strip()
    if not t:
        return None, None
    for sep in (" - ", " – ", " to ", "—"):
        if sep in t:
            a, b = t.split(sep, 1)
            a, b = a.strip(), b.strip()
            if a and b:
                return a, b
    if "-" in t and t.count("-") >= 2:
        parts = re.split(r"\s*-\s*", t, maxsplit=1)
        if len(parts) == 2 and parts[0].strip() and parts[1].strip():
            return parts[0].strip(), parts[1].strip()
    return t, None


def parse_guests(text: str) -> str | None:
    m = re.search(r"\d+", text)
    return m.group(0) if m else None


def start_booking(session: UserSession) -> str:
    session.mode = "booking"
    session.city = None
    session.check_in = None
    session.check_out = None
    session.guests = None
    session.step = "city"
    return "Hangi şehirde konaklamak istersiniz?"


def reset_session(session: UserSession) -> None:
    session.mode = "idle"
    session.city = None
    session.check_in = None
    session.check_out = None
    session.guests = None
    session.step = "city"


def booking_reply(session: UserSession, message: str) -> str:
    msg = message.strip()
    if not msg:
        return "Lütfen bir yanıt yazın."

    if session.step == "city":
        session.city = msg
        session.step = "dates"
        return (
            "Giriş ve çıkış tarihlerinizi yazın "
            "(ör. 2026-04-10 - 2026-04-15 veya 10.04.2026 - 15.04.2026)."
        )

    if session.step == "dates":
        ci, co = parse_dates(msg)
        if not ci:
            return "Tarihleri anlayamadım; lütfen iki tarihi birlikte veya aralık olarak yazın."
        session.check_in = ci
        session.check_out = co if co else ci
        session.step = "guests"
        return "Kaç misafir? (sayı yazın, örn. 2)"

    if session.step == "guests":
        g = parse_guests(msg)
        if not g:
            return "Lütfen misafir sayısını rakamla yazın (ör. 2)."
        session.guests = g
        summary = (
            "Özet (demo):\n"
            f"- Şehir: {session.city}\n"
            f"- Giriş: {session.check_in}\n"
            f"- Çıkış: {session.check_out}\n"
            f"- Misafir: {session.guests}\n\n"
            "Bu bir demodur; gerçek ödeme veya kesin rezervasyon yoktur. "
            "Yeni rezervasyon için yine rezervasyon isteği gönderebilirsiniz."
        )
        reset_session(session)
        return summary

    return "Bir sorun oluştu; yeni rezervasyon için tekrar deneyin."
