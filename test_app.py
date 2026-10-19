import pytest

from app import create_app


@pytest.fixture
def client(tmp_path):
    app = create_app({"TESTING": True, "DATABASE": str(tmp_path / "students.db")})
    with app.test_client() as test_client:
        yield test_client


def test_student_crud_endpoints(client):
    created = client.post(
        "/students",
        json={"name": "Rahul", "attendance": 85, "marks": 78},
    )
    assert created.status_code == 201
    student = created.get_json()
    student_id = student["id"]
    assert student["name"] == "Rahul"
    assert student["attendance"] == 85
    assert student["marks"] == 78
    assert student["created_at"]

    assert client.get("/students").get_json() == [student]
    assert client.get(f"/students/{student_id}").get_json() == student

    updated = client.put(f"/students/{student_id}", json={"marks": 91})
    assert updated.status_code == 200
    assert updated.get_json()["marks"] == 91
    assert updated.get_json()["name"] == "Rahul"

    assert client.delete(f"/students/{student_id}").status_code == 204
    assert client.get(f"/students/{student_id}").status_code == 404


@pytest.mark.parametrize(
    "payload",
    [
        {"name": "", "attendance": 85, "marks": 78},
        {"name": "Rahul", "attendance": -1, "marks": 78},
        {"name": "Rahul", "attendance": 101, "marks": 78},
        {"name": "Rahul", "attendance": 85.5, "marks": 78},
        {"name": "Rahul", "attendance": 85, "marks": 101},
        {"name": "Rahul", "attendance": True, "marks": 78},
        {"name": "Rahul", "attendance": 85},
    ],
)
def test_create_rejects_invalid_student_data(client, payload):
    response = client.post("/students", json=payload)
    assert response.status_code == 400
    assert "error" in response.get_json()


def test_update_rejects_invalid_data_and_missing_students(client):
    assert client.put("/students/999", json={"marks": 50}).status_code == 404
    assert client.put("/students/999", json={}).status_code == 400
    assert client.delete("/students/999").status_code == 404
    assert client.get("/students/999").status_code == 404


def test_invalid_json_body_returns_bad_request(client):
    response = client.post("/students", data="not-json", content_type="text/plain")
    assert response.status_code == 400
    assert "error" in response.get_json()
