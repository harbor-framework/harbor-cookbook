import sys

sys.path.insert(0, "/app")

from deduplicate import deduplicate


def test_basic_dedup():
    records = [
        {"id": 1, "email": "alice@example.com", "name": "Alice"},
        {"id": 2, "email": "bob@example.com", "name": "Bob"},
        {"id": 3, "email": "ALICE@example.com", "name": "Alice A."},
    ]
    result = deduplicate(records)
    assert len(result) == 2
    emails = {r["email"].lower() for r in result}
    assert emails == {"alice@example.com", "bob@example.com"}


def test_keeps_highest_id():
    records = [
        {"id": 1, "email": "alice@example.com"},
        {"id": 5, "email": "alice@example.com"},
        {"id": 3, "email": "alice@example.com"},
    ]
    result = deduplicate(records)
    assert len(result) == 1
    assert result[0]["id"] == 5


def test_sorted_by_id():
    records = [
        {"id": 10, "email": "z@example.com"},
        {"id": 1, "email": "a@example.com"},
        {"id": 5, "email": "m@example.com"},
    ]
    result = deduplicate(records)
    ids = [r["id"] for r in result]
    assert ids == [1, 5, 10]


def test_case_insensitive():
    records = [
        {"id": 1, "email": "User@Example.COM"},
        {"id": 2, "email": "user@example.com"},
    ]
    result = deduplicate(records)
    assert len(result) == 1
    assert result[0]["id"] == 2


def test_preserves_extra_fields():
    records = [
        {"id": 1, "email": "a@b.com", "role": "admin", "active": True},
    ]
    result = deduplicate(records)
    assert result[0]["role"] == "admin"
    assert result[0]["active"] is True


def test_empty_input():
    assert deduplicate([]) == []


def test_single_record():
    records = [{"id": 42, "email": "only@one.com"}]
    result = deduplicate(records)
    assert len(result) == 1
    assert result[0]["id"] == 42
