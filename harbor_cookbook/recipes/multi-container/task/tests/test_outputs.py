"""Tests that the agent fetched items from the API and wrote them to a file."""

import json
from pathlib import Path


def test_items_file_exists():
    assert Path("/app/items.json").exists(), "items.json was not created"


def test_items_file_is_valid_json():
    content = Path("/app/items.json").read_text()
    items = json.loads(content)
    assert isinstance(items, list), "items.json should contain a JSON array"


def test_harbor_item_present():
    content = Path("/app/items.json").read_text()
    items = json.loads(content)
    names = [item["name"] for item in items]
    assert "harbor" in names, f"'harbor' not found in item names: {names}"
