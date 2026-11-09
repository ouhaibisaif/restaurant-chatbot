from app.services.reservation_parser import missing_reservation_fields, parse_reservation_details


def test_full_english_request():
    details = parse_reservation_details(
        "My name is Sami Ben Ali, phone +216 20 123 456, table for 4 people on 2026-12-05 at 7pm"
    )
    assert details == {
        "name": "Sami Ben Ali",
        "phone": "+216 20 123 456",
        "people": 4,
        "reservation_date": "2026-12-05",
        "reservation_time": "19:00",
    }


def test_phone_digits_are_not_read_as_party_size():
    details = parse_reservation_details("Call me on +216 20 123 456, we are 3 people")
    assert details["people"] == 3


def test_time_alone_is_not_read_as_party_size():
    assert "people" not in parse_reservation_details("Can I book at 7pm?")


def test_french_request():
    details = parse_reservation_details("Je m'appelle Leila, 4 personnes le 05/12/2026 à 20h30")
    assert details["name"] == "Leila"
    assert details["people"] == 4
    assert details["reservation_date"] == "2026-12-05"
    assert details["reservation_time"] == "20:30"


def test_12am_and_12pm():
    assert parse_reservation_details("at 12am")["reservation_time"] == "00:00"
    assert parse_reservation_details("at 12pm")["reservation_time"] == "12:00"


def test_missing_fields():
    assert missing_reservation_fields({"name": "Sami", "people": 2}) == ["phone", "reservation_date", "reservation_time"]
