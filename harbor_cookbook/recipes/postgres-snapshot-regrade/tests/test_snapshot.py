"""Grade only the captured database artifact, including on regrade."""

import json
from pathlib import Path

import pytest


@pytest.fixture(scope="module")
def snapshot():
    state = json.loads(Path("/snapshot/state.json").read_text())
    assert set(state) == {"schema_version", "customers", "orders", "line_items"}
    assert type(state["schema_version"]) is int
    assert state["schema_version"] == 1
    return state


def test_customers_preserved(snapshot):
    assert snapshot["customers"] == [
        {"id": 1, "name": "Ada"},
        {"id": 2, "name": "Grace"},
    ]


def test_line_items_preserved(snapshot):
    assert snapshot["line_items"] == [
        {"id": 1, "order_id": 101, "quantity": 2, "unit_price_cents": 1200},
        {"id": 2, "order_id": 101, "quantity": 1, "unit_price_cents": 100},
        {"id": 3, "order_id": 102, "quantity": 1, "unit_price_cents": 2999},
        {"id": 4, "order_id": 102, "quantity": 2, "unit_price_cents": 250},
        {"id": 5, "order_id": 104, "quantity": 3, "unit_price_cents": 500},
    ]


def test_orders_preserved(snapshot):
    orders = snapshot["orders"]
    assert [row["id"] for row in orders] == [101, 102, 103, 104]
    assert [row["customer_id"] for row in orders] == [1, 2, 1, 2]
    for row in orders:
        assert set(row) == {"id", "customer_id", "total_cents"}
        assert all(type(value) is int for value in row.values())


def test_first_order_total(snapshot):
    assert snapshot["orders"][0]["total_cents"] == 2500


def test_second_order_total(snapshot):
    assert snapshot["orders"][1]["total_cents"] == 3499


def test_empty_order_total(snapshot):
    assert snapshot["orders"][2]["total_cents"] == 0


def test_correct_order_total_preserved(snapshot):
    assert snapshot["orders"][3]["total_cents"] == 1500
