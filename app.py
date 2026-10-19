students = {
    101: {"name": "Rahul", "attendance": 85, "marks": 78},
    102: {"name": "Priya", "attendance": 90, "marks": 88}
}

def display_student(student_id):
    if student_id in students:
        student = students[student_id]
        print("\nStudent ID:", student_id)
        print("Name:", student["name"])
        print("Attendance:", student["attendance"], "%")
        print("Marks:", student["marks"])
    else:
        print("Student not found.")

def display_all_students():
    print("\nAll Students")
    for student_id, student in students.items():
        print(student_id, "-", student["name"])

if __name__ == "__main__":
    print("College ERP System")
    student_id = int(input("Enter Student ID: "))
    display_student(student_id)
    display_all_students()
