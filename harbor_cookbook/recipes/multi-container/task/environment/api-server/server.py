"""Simple REST API that stores items in memory."""

from flask import Flask, jsonify, request

app = Flask(__name__)

items: list[dict] = [
    {"id": 1, "name": "alpha"},
    {"id": 2, "name": "bravo"},
]
next_id = 3


@app.get("/items")
def get_items():
    return jsonify(items)


@app.post("/items")
def create_item():
    global next_id
    data = request.get_json()
    item = {"id": next_id, "name": data["name"]}
    next_id += 1
    items.append(item)
    return jsonify(item), 201


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
