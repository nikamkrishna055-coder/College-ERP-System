from app import students, display_student, display_all_students

def test_student_exists():
    assert 101 in students
    assert 102 in students

def test_student_details():
    assert students[101]["name"] == "Rahul"
    assert students[101]["attendance"] == 85
    assert students[101]["marks"] == 78

def test_second_student():
    assert students[102]["name"] == "Priya"
    assert students[102]["attendance"] == 90
    assert students[102]["marks"] == 88
