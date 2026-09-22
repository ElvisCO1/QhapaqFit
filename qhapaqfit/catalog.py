import json
import sqlite3
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def normalize(value):
    return "".join(c for c in unicodedata.normalize("NFD", value.casefold())
                   if unicodedata.category(c) != "Mn")


def load_catalog():
    exercises = json.loads((ROOT / "data/exercises.json").read_text(encoding="utf-8"))
    ids = set()
    for exercise in exercises:
        identifier = exercise["id"]
        if identifier in ids:
            raise ValueError(f"Duplicate exercise: {identifier}")
        ids.add(identifier)
        for key in ("name", "english_name", "summary", "group", "equipment", "muscles",
                    "level", "description", "steps", "mistakes", "video", "image"):
            if not exercise.get(key):
                raise ValueError(f"Missing {key}: {identifier}")
    return exercises


def matches(exercise, query):
    terms = normalize(query).split()
    text = normalize(" ".join([exercise["name"], exercise["english_name"],
                               exercise["equipment"], *exercise["muscles"]]))
    return all(term in text for term in terms)


class Favorites:
    def __init__(self, path):
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        self.connection = sqlite3.connect(path)
        self.connection.execute("CREATE TABLE IF NOT EXISTS favorites (exercise_id TEXT PRIMARY KEY)")

    def all(self):
        return {row[0] for row in self.connection.execute("SELECT exercise_id FROM favorites")}

    def set(self, identifier, enabled):
        with self.connection:
            if enabled:
                self.connection.execute("INSERT OR IGNORE INTO favorites VALUES (?)", (identifier,))
            else:
                self.connection.execute("DELETE FROM favorites WHERE exercise_id = ?", (identifier,))

    def close(self):
        self.connection.close()
