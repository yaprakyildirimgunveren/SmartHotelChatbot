from app.services.room_recommendation import recommend_room


def test_recommend_for_single_guest():
    text = recommend_room("Istanbul", "2026-07-10", 1)
    assert "Standart Oda" in text
    assert "EUR" in text


def test_recommend_for_family_room():
    text = recommend_room("Kapadokya", "10.04.2026", 4)
    assert "Aile Odası" in text
    assert "filtreleyebilirim" in text
