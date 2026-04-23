from __future__ import annotations

import re
from datetime import datetime
from typing import Any


def _extract_month(check_in: str | None) -> int | None:
    if not check_in:
        return None

    patterns = (
        (r"^\s*(\d{4})-(\d{2})-(\d{2})\s*$", "%Y-%m-%d"),
        (r"^\s*(\d{2})\.(\d{2})\.(\d{4})\s*$", "%d.%m.%Y"),
        (r"^\s*(\d{2})/(\d{2})/(\d{4})\s*$", "%d/%m/%Y"),
    )
    for pattern, fmt in patterns:
        if re.match(pattern, check_in):
            try:
                return datetime.strptime(check_in.strip(), fmt).month
            except ValueError:
                return None
    return None


def _city_price_multiplier(city: str) -> float:
    city_norm = city.strip().lower()
    high_demand = {"istanbul", "bodrum", "çeşme", "cesme", "antalya"}
    medium_demand = {"izmir", "ankara", "kapadokya", "fethiye"}
    if city_norm in high_demand:
        return 1.25
    if city_norm in medium_demand:
        return 1.1
    return 1.0


def _season_multiplier(month: int | None) -> float:
    if month is None:
        return 1.0
    if month in {6, 7, 8, 9}:
        return 1.2
    if month in {12, 1}:
        return 1.08
    return 1.0


_ROOM_INVENTORY = [
    {"hotel": "Golden Bosphorus", "city": "istanbul", "room_type": "Deluxe Double", "capacity": 2, "price_eur": 178, "breakfast": True, "refundable": True, "view": "sea"},
    {"hotel": "Cappadocia Stone", "city": "kapadokya", "room_type": "Aile Odası", "capacity": 4, "price_eur": 142, "breakfast": True, "refundable": False, "view": "city"},
    {"hotel": "Antalya Marina", "city": "antalya", "room_type": "Standart Oda", "capacity": 2, "price_eur": 130, "breakfast": False, "refundable": True, "view": "sea"},
    {"hotel": "Ege Comfort", "city": "izmir", "room_type": "Aile Odası", "capacity": 4, "price_eur": 124, "breakfast": True, "refundable": True, "view": "city"},
    {"hotel": "Bodrum Blue", "city": "bodrum", "room_type": "Bağlantılı Aile Suiti", "capacity": 6, "price_eur": 245, "breakfast": True, "refundable": True, "view": "sea"},
]


def _normalize_city(city: str) -> str:
    return city.strip().lower()


def parse_preferences(text: str) -> dict[str, bool]:
    low = text.lower()
    breakfast = any(k in low for k in ("kahvaltı", "kahvalti", "breakfast"))
    refundable = any(k in low for k in ("iptal", "refund", "esnek", "flex"))
    sea_view = any(k in low for k in ("deniz", "sea view", "manzara"))
    return {"breakfast": breakfast, "refundable": refundable, "sea_view": sea_view}


def recommend_rooms(
    city: str,
    check_in: str | None,
    guests: int,
    preferences: str,
    max_budget: int | None = None,
) -> list[dict[str, Any]]:
    pref = parse_preferences(preferences)
    city_norm = _normalize_city(city)
    month = _extract_month(check_in)
    season = _season_multiplier(month)
    city_mul = _city_price_multiplier(city_norm)

    candidates: list[dict[str, Any]] = []
    for room in _ROOM_INVENTORY:
        if room["capacity"] < guests:
            continue
        if room["city"] != city_norm:
            continue
        if pref["breakfast"] and not room["breakfast"]:
            continue
        if pref["refundable"] and not room["refundable"]:
            continue
        if pref["sea_view"] and room["view"] != "sea":
            continue

        score = 100 - (room["price_eur"] * season * city_mul) / 10
        score += 8 if room["capacity"] == guests else 0
        score += 4 if room["breakfast"] else 0
        score += 3 if room["refundable"] else 0
        final_price = int(room["price_eur"] * season * city_mul)
        if max_budget is not None and final_price > max_budget:
            continue
        candidates.append(
            {
                "hotel": room["hotel"],
                "room_type": room["room_type"],
                "price_eur": final_price,
                "breakfast": room["breakfast"],
                "refundable": room["refundable"],
                "view": room["view"],
                "score": round(score, 2),
            }
        )

    if not candidates:
        base_price = int(95 * season * city_mul * max(1, guests * 0.8))
        fallback_room = "Aile Odası" if guests >= 3 else "Deluxe Double"
        if max_budget is not None and max(base_price, 60) > max_budget:
            return []
        return [
            {
                "hotel": f"{city.title()} Central",
                "room_type": fallback_room,
                "price_eur": max(base_price, 60),
                "breakfast": pref["breakfast"],
                "refundable": pref["refundable"],
                "view": "city",
                "score": 50.0,
            }
        ]

    candidates.sort(key=lambda x: (-x["score"], x["price_eur"]))
    return candidates[:3]


def recommendations_to_text(items: list[dict[str, Any]]) -> str:
    if not items:
        return "Kriterlerinize uygun oda bulunamadı. Bütçeyi artırabilir veya tercihleri gevşetebilirsiniz."
    lines = ["Oda önerileri:"]
    for idx, item in enumerate(items, start=1):
        lines.append(
            f"- {idx}) {item['hotel']} | {item['room_type']} | {item['price_eur']} EUR/gece | "
            f"kahvaltı: {'evet' if item['breakfast'] else 'hayır'} | "
            f"esnek iptal: {'evet' if item['refundable'] else 'hayır'}"
        )
    lines.append("- İsterseniz bütçe aralığına göre yeniden sıralayabilirim.")
    return "\n".join(lines)
