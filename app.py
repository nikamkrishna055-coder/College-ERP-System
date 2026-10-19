import os
import sqlite3
from pathlib import Path

from flask import Flask, jsonify, request


def create_app(test_config=None):
    app = Flask(__name__)
    default_db = Path(__file__).with_name("students.db")
    app.config.from_mapping(DATABASE=os.environ.get("DATABASE", str(default_db)))
    if test_config:
        app.config.update(test_config)

    def connect_db():
        connection = sqlite3.connect(app.config["DATABASE"])
        connection.row_factory = sqlite3.Row
        return connection

    def initialize_db():
        database = app.config["DATABASE"]
        Path(database).parent.mkdir(parents=True, exist_ok=True)
        with connect_db() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS students (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    attendance INTEGER NOT NULL CHECK (attendance BETWEEN 0 AND 100),
                    marks INTEGER NOT NULL CHECK (marks BETWEEN 0 AND 100),
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                )
                """
            )

    def student_dict(row):
        return {
            "id": row["id"],
            "name": row["name"],
            "attendance": row["attendance"],
            "marks": row["marks"],
            "created_at": row["created_at"],
        }

    def parse_student(data, *, partial=False):
        if not isinstance(data, dict):
            return None, "Request body must be a JSON object."

        values = {}
        for field in ("name", "attendance", "marks"):
            if field not in data:
                if partial:
                    continue
                return None, f"Missing required field: {field}."
            value = data[field]
            if field == "name":
                if not isinstance(value, str) or not value.strip():
                    return None, "Name must be a non-empty string."
                values[field] = value.strip()
            else:
                if isinstance(value, bool) or not isinstance(value, int) or not 0 <= value <= 100:
                    return None, f"{field.capitalize()} must be an integer from 0 to 100."
                values[field] = value
        return values, None

    @app.get("/students")
    def get_students():
        with connect_db() as connection:
            rows = connection.execute(
                "SELECT id, name, attendance, marks, created_at FROM students ORDER BY id"
            ).fetchall()
        return jsonify([student_dict(row) for row in rows])

    @app.get("/students/<int:student_id>")
    def get_student(student_id):
        with connect_db() as connection:
            row = connection.execute(
                "SELECT id, name, attendance, marks, created_at FROM students WHERE id = ?",
                (student_id,),
            ).fetchone()
        if row is None:
            return jsonify(error="Student not found."), 404
        return jsonify(student_dict(row))

    @app.post("/students")
    def create_student():
        values, error = parse_student(request.get_json(silent=True))
        if error:
            return jsonify(error=error), 400
        with connect_db() as connection:
            cursor = connection.execute(
                "INSERT INTO students (name, attendance, marks) VALUES (?, ?, ?)",
                (values["name"], values["attendance"], values["marks"]),
            )
            row = connection.execute(
                "SELECT id, name, attendance, marks, created_at FROM students WHERE id = ?",
                (cursor.lastrowid,),
            ).fetchone()
        return jsonify(student_dict(row)), 201

    @app.put("/students/<int:student_id>")
    def update_student(student_id):
        values, error = parse_student(request.get_json(silent=True), partial=True)
        if error:
            return jsonify(error=error), 400
        if not values:
            return jsonify(error="Provide at least one student field to update."), 400

        with connect_db() as connection:
            existing = connection.execute(
                "SELECT id, name, attendance, marks, created_at FROM students WHERE id = ?",
                (student_id,),
            ).fetchone()
            if existing is None:
                return jsonify(error="Student not found."), 404
            values = {
                "name": values.get("name", existing["name"]),
                "attendance": values.get("attendance", existing["attendance"]),
                "marks": values.get("marks", existing["marks"]),
            }
            connection.execute(
                "UPDATE students SET name = ?, attendance = ?, marks = ? WHERE id = ?",
                (values["name"], values["attendance"], values["marks"], student_id),
            )
            row = connection.execute(
                "SELECT id, name, attendance, marks, created_at FROM students WHERE id = ?",
                (student_id,),
            ).fetchone()
        return jsonify(student_dict(row))

    @app.delete("/students/<int:student_id>")
    def delete_student(student_id):
        with connect_db() as connection:
            cursor = connection.execute("DELETE FROM students WHERE id = ?", (student_id,))
        if cursor.rowcount == 0:
            return jsonify(error="Student not found."), 404
        return "", 204

    initialize_db()
    return app


app = create_app()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", "5000")))
