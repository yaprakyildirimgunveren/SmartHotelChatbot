from __future__ import annotations

import re
import uuid
from dataclasses import dataclass
from typing import Any, Literal

from .room_recommendation import recommendations_to_text, recommend_rooms

Mode = Literal["idle", "booking"]
Step = Literal["city", "dates", "guests", "preferences", "budget", "select", "complete"]


@dataclass
class UserSession:
    mode: Mode = "idle"
    city: str | None = None
    check_in: str | None = None
    check_out: str | None = None
    guests: str | None = None
    preferences: str | None = None
    max_budget: int | None = None
    last_recommendations: list[dict[str, Any]] | None = None
    selected_recommendation: dict[str, Any] | None = None
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


def parse_budget(text: str) -> int | None:
    m = re.search(r"\d+", text)
    if not m:
        return None
    return int(m.group(0))


def parse_selection(text: str, max_index: int) -> int | None:
    m = re.search(r"\d+", text)
    if not m:
        return None
    choice = int(m.group(0))
    if choice < 1 or choice > max_index:
        return None
    return choice


def start_booking(session: UserSession) -> str:
    session.mode = "booking"
    session.city = None
    session.check_in = None
    session.check_out = None
    session.guests = None
    session.preferences = None
    session.max_budget = None
    session.last_recommendations = []
    session.selected_recommendation = None
    session.step = "city"
    return "Hangi şehirde konaklamak istersiniz?"


def reset_session(session: UserSession) -> None:
    session.mode = "idle"
    session.city = None
    session.check_in = None
    session.check_out = None
    session.guests = None
    session.preferences = None
    session.max_budget = None
    session.last_recommendations = []
    session.selected_recommendation = None
    session.step = "city"


def booking_reply(session: UserSession, message: str) -> tuple[str, list[dict[str, Any]]]:
    msg = message.strip()
    if not msg:
        return "Lütfen bir yanıt yazın.", []

    if session.step == "city":
        session.city = msg
        session.step = "dates"
        return (
            "Giriş ve çıkış tarihlerinizi yazın "
            "(ör. 2026-04-10 - 2026-04-15 veya 10.04.2026 - 15.04.2026)."
        ), []

    if session.step == "dates":
        ci, co = parse_dates(msg)
        if not ci:
            return "Tarihleri anlayamadım; lütfen iki tarihi birlikte veya aralık olarak yazın.", []
        session.check_in = ci
        session.check_out = co if co else ci
        session.step = "guests"
        return "Kaç misafir? (sayı yazın, örn. 2)", []

    if session.step == "guests":
        g = parse_guests(msg)
        if not g:
            return "Lütfen misafir sayısını rakamla yazın (ör. 2).", []
        session.guests = g
        session.step = "preferences"
        return (
            "Tercihleriniz var mı? (örn. kahvaltı dahil, esnek iptal, deniz manzarası) "
            "Yoksa 'yok' yazabilirsiniz."
        ), []

    if session.step == "preferences":
        session.preferences = msg
        session.step = "budget"
        return "Maksimum gecelik bütçeniz nedir? (EUR, örn. 180)", []

    if session.step == "budget":
        budget = parse_budget(msg)
        if not budget:
            return "Bütçeyi rakamla yazın (örn. 180).", []
        session.max_budget = budget
        recommendations = recommend_rooms(
            city=session.city or "Genel",
            check_in=session.check_in,
            guests=int(session.guests or "1"),
            preferences="" if (session.preferences or "").lower() == "yok" else (session.preferences or ""),
            max_budget=budget,
        )
        session.last_recommendations = recommendations
        recommendation_text = recommendations_to_text(recommendations)
        session.step = "select"
        if not recommendations:
            summary = (
                "Özet (demo):\n"
                f"- Şehir: {session.city}\n"
                f"- Giriş: {session.check_in}\n"
                f"- Çıkış: {session.check_out}\n"
                f"- Misafir: {session.guests}\n"
                f"- Maksimum bütçe: {session.max_budget} EUR\n\n"
                f"{recommendation_text}\n\n"
                "Bu bir demodur; gerçek ödeme veya kesin rezervasyon yoktur. "
                "Yeni rezervasyon için yine rezervasyon isteği gönderebilirsiniz."
            )
            reset_session(session)
            return summary, []
        return (
            f"{recommendation_text}\n\n"
            "Bu 3 öneriden birini seçmek için sadece numarasını yazın (örn. 1)."
        ), recommendations

    if session.step == "select":
        options = session.last_recommendations or []
        if not options:
            reset_session(session)
            return "Öneri listesi bulunamadı; rezervasyonu yeniden başlatabilirsiniz.", []
        picked = parse_selection(msg, len(options))
        if not picked:
            return f"Lütfen 1 ile {len(options)} arasında bir seçim yapın.", options
        session.selected_recommendation = options[picked - 1]
        summary = (
            "Özet (demo):\n"
            f"- Şehir: {session.city}\n"
            f"- Giriş: {session.check_in}\n"
            f"- Çıkış: {session.check_out}\n"
            f"- Misafir: {session.guests}\n"
            f"- Maksimum bütçe: {session.max_budget} EUR\n"
            f"- Seçilen öneri: {session.selected_recommendation['hotel']} / "
            f"{session.selected_recommendation['room_type']} / "
            f"{session.selected_recommendation['price_eur']} EUR-gece\n\n"
            f"{recommendations_to_text(options)}\n\n"
            "Bu bir demodur; gerçek ödeme veya kesin rezervasyon yoktur. "
            "Yeni rezervasyon için yine rezervasyon isteği gönderebilirsiniz."
        )
        result = options
        reset_session(session)
        return summary, result

    return "Bir sorun oluştu; yeni rezervasyon için tekrar deneyin.", []
