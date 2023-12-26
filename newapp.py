from flask import Flask, render_template, jsonify, request
from flask_sqlalchemy import SQLAlchemy
import csv
import os

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///students.db"
db = SQLAlchemy(app)


class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(500), unique=True, nullable=False)
    gender = db.Column(db.String(10), nullable=False)
    part_time_job = db.Column(db.String(10), nullable=False)
    absence_days = db.Column(db.Integer, nullable=False)
    weekly_self_study_hours = db.Column(db.Integer, nullable=False)
    career_aspiration = db.Column(db.String(100), nullable=False)


def get_student_list(students):
    students_list = []
    for student in students:
        student_data = {
            "id": student.id,
            "first_name": student.first_name,
            "last_name": student.last_name,
            "email": student.email,
            "gender": student.gender,
            "part_time_job": student.part_time_job,
            "absence_days": student.absence_days,
            "weekly_self_study_hours": student.weekly_self_study_hours,
            "career_aspiration": student.career_aspiration,
        }
        students_list.append(student_data)
    return students_list


# Load data from CSV file and populate the database
def populate_database():
    with open("samplefile.csv", "r") as file:
        csv_reader = csv.DictReader(file)
        for row in csv_reader:
            student = Student(
                first_name=row["first_name"],
                last_name=row["last_name"],
                email=row["email"],
                gender=row["gender"],
                part_time_job=row["part_time_job"].lower() == "true",
                absence_days=int(row["absence_days"]),
                weekly_self_study_hours=int(row["weekly_self_study_hours"]),
                career_aspiration=row["career_aspiration"],
            )
            db.session.add(student)
        db.session.commit()


# Uncomment the line below to populate the database initially
if not os.path.exists("instance/students.db"):
    populate_database()


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/students")
def students():
    draw = int(request.args.get("draw", 1))
    start = int(request.args.get("start", 0))
    length = int(request.args.get("length", 10))
    sort_column_index = int(request.args.get("order[0][column]", 0))
    sort_column_name = request.args.get(f"columns[{sort_column_index}][data]", "id")
    sort_direction = request.args.get("order[0][dir]", "asc")
    start = int(start / length) + 1


    search_value = request.args.get("search[value]", "")

    # Validate sort_direction
    if sort_direction not in ["asc", "desc"]:
        return jsonify({"error": 'Invalid sort direction. Use "asc" or "desc".'}), 400

    # Query and paginate the data from the database with filtering
    students_query = Student.query.filter(
        (Student.first_name.ilike(f"%{search_value}%")) |
        (Student.last_name.ilike(f"%{search_value}%")) |
        (Student.email.ilike(f"%{search_value}")) |
        (Student.gender.ilike(f"%{search_value}")) |
        (Student.part_time_job.ilike(f"%{search_value}")) |
        (Student.absence_days.ilike(f"%{search_value}")) |
        (Student.weekly_self_study_hours.ilike(f"%{search_value}")) |
        (Student.career_aspiration.ilike(f"%{search_value}"))
    ).order_by(
        getattr(Student, sort_column_name).asc() if sort_direction == "asc" else getattr(Student, sort_column_name).desc()
    ).paginate(page=start, per_page=length, error_out=False)

    # Convert query results to a list of dictionaries
    students_list = get_student_list(students_query.items)

    response = {
        "draw": draw,
        "recordsTotal": students_query.total,
        "recordsFiltered": students_query.total,
        "data": students_list,
    }

    return jsonify(response)


@app.route("/student/<int:id>")
def student(id):
    student = Student.query.get(id)
    return jsonify(
        {
            "id": student.id,
            "first_name": student.first_name,
            "last_name": student.last_name,
            "email": student.email,
            "gender": student.gender,
            "part_time_job": student.part_time_job,
            "absence_days": student.absence_days,
            "weekly_self_study_hours": student.weekly_self_study_hours,
            "career_aspiration": student.career_aspiration,
        }
    )


@app.route("/student/delete/<int:id>", methods=["DELETE"])
def delete(id):
    student = Student.query.get(id)
    if student:
        db.session.delete(student)
        db.session.commit()
        return jsonify({"message": "Student Deleted Successfully"})
    else:
        return jsonify({"error": "Student Not Found!"})


@app.route("/student/update/<int:id>", methods=["PUT"])
def update_student(id):
    student = Student.query.get(id)

    if student:
        data = request.form  # Use request.form to get data from the form
        student.first_name = data.get("first_name", student.first_name)
        student.last_name = data.get("last_name", student.last_name)
        student.email = data.get("email", student.email)
        student.gender = data.get("gender", student.gender)
        student.part_time_job = data.get("part_time_job", student.part_time_job)
        student.absence_days = data.get("absence_days", student.absence_days)
        student.weekly_self_study_hours = data.get(
            "weekly_self_study_hours", student.weekly_self_study_hours
        )
        student.career_aspiration = data.get(
            "career_aspiration", student.career_aspiration
        )

        db.session.commit()

        return jsonify({"message": f"Student with ID {id} updated successfully"})
    else:
        return jsonify({"error": "Student not found"}), 404


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        app.run(debug=True)
