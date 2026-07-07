from flask import Blueprint, jsonify, request
from extensions import db
from courses.models import Course

courses_bp = Blueprint(
    "courses",
    __name__,
    url_prefix="/api/courses"
)


def make_response_json(data, status_code=200):
    return jsonify({
        "status": "success",
        "data": data
    }), status_code


# -----------------------------
# GET ALL COURSES
# -----------------------------
@courses_bp.route("/", methods=["GET"])
def get_courses():
    courses = Course.query.all()

    return make_response_json(
        [course.to_dict() for course in courses]
    )


# -----------------------------
# CREATE COURSE
# -----------------------------
@courses_bp.route("/", methods=["POST"])
def create_course():

    data = request.get_json()

    if not data:
        return jsonify({
            "status": "error",
            "message": "Request must be JSON"
        }), 400

    required_fields = ["name", "code", "credits", "department_id"]

    for field in required_fields:
        if field not in data:
            return jsonify({
                "status": "error",
                "message": f"{field} is required"
            }), 400

    course = Course(
        name=data["name"],
        code=data["code"],
        credits=data["credits"],
        department_id=data["department_id"]
    )

    db.session.add(course)
    db.session.commit()

    return make_response_json(course.to_dict(), 201)


# -----------------------------
# GET COURSE BY ID
# -----------------------------
@courses_bp.route("/<int:course_id>/", methods=["GET"])
def get_course(course_id):

    course = Course.query.get_or_404(course_id)

    return make_response_json(course.to_dict())


# -----------------------------
# UPDATE COURSE
# -----------------------------
@courses_bp.route("/<int:course_id>/", methods=["PUT"])
def update_course(course_id):

    course = Course.query.get_or_404(course_id)

    data = request.get_json()

    if not data:
        return jsonify({
            "status": "error",
            "message": "Request must be JSON"
        }), 400

    course.name = data.get("name", course.name)
    course.code = data.get("code", course.code)
    course.credits = data.get("credits", course.credits)
    course.department_id = data.get("department_id", course.department_id)

    db.session.commit()

    return make_response_json(course.to_dict())


# -----------------------------
# DELETE COURSE
# -----------------------------
@courses_bp.route("/<int:course_id>/", methods=["DELETE"])
def delete_course(course_id):

    course = Course.query.get_or_404(course_id)

    db.session.delete(course)
    db.session.commit()

    return jsonify({
        "status": "success",
        "message": "Course deleted successfully"
    }), 200


# -----------------------------
# GET STUDENTS ENROLLED IN A COURSE
# -----------------------------
@courses_bp.route("/<int:course_id>/students/", methods=["GET"])
def get_course_students(course_id):

    course = Course.query.get_or_404(course_id)

    students = [
        enrollment.student.to_dict()
        for enrollment in course.enrollments
    ]

    return make_response_json(students)