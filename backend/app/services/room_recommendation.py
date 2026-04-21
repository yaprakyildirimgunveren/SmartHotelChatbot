from __future__ import annotations

import re
from datetime import datetime


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


def recommend_room(city: str, check_in: str | None, guests: int) -> str:
    base_price = 85
    if guests <= 1:
        room_type = "Standart Oda"
        capacity_note = "1 misafir"
    elif guests == 2:
        room_type = "Deluxe Double"
        capacity_note = "2 misafir"
    elif guests <= 4:
        room_type = "Aile Odası"
        capacity_note = f"{guests} misafir"
    else:
        room_type = "Bağlantılı Aile Suiti"
        capacity_note = f"{guests} misafir"

    month = _extract_month(check_in)
    estimated_price = int(base_price * _city_price_multiplier(city) * _season_multiplier(month) * max(1, guests * 0.85))
    low = max(estimated_price - 20, 50)
    high = estimated_price + 25

    return (
        "Oda önerisi:\n"
        f"- Önerilen tip: {room_type} ({capacity_note})\n"
        f"- Tahmini gecelik fiyat aralığı: {low} - {high} EUR\n"
        "- İsterseniz kahvaltı dahil veya iptal edilebilir seçenekleri de filtreleyebilirim."
    )
