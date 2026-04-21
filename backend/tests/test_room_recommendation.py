from app.services.room_recommendation import recommendations_to_text, recommend_rooms


def test_recommend_for_single_guest():
    items = recommend_rooms("Istanbul", "2026-07-10", 1, "")
    assert len(items) >= 1
    assert "price_eur" in items[0]


def test_recommend_for_family_room():
    items = recommend_rooms("Kapadokya", "10.04.2026", 4, "kahvaltı")
    text = recommendations_to_text(items)
    assert len(items) >= 1
    assert "Oda önerileri" in text
