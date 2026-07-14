from flask import Flask, jsonify, request

from database import db
from models import Course

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///course.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)

with app.app_context():
    db.create_all()


@app.route("/")
def home():
    return {
        "service": "Course Service",
        "status": "Running"
    }


@app.route("/api/courses", methods=["GET"])
def get_courses():

    courses = Course.query.all()

    return jsonify(
        [course.to_dict() for course in courses]
    )


@app.route("/api/courses/<int:id>", methods=["GET"])
def get_course(id):

    course = Course.query.get(id)

    if not course:
        return jsonify({
            "message": "Course not found"
        }), 404

    return jsonify(course.to_dict())


@app.route("/api/courses", methods=["POST"])
def create_course():

    data = request.get_json()

    course = Course(
        name=data["name"],
        code=data["code"],
        credits=data["credits"],
        department=data["department"]
    )

    db.session.add(course)

    db.session.commit()

    return jsonify(course.to_dict()), 201


@app.route("/api/courses/<int:id>", methods=["PUT"])
def update_course(id):

    course = Course.query.get(id)

    if not course:
        return jsonify({
            "message": "Course not found"
        }), 404

    data = request.get_json()

    course.name = data["name"]
    course.code = data["code"]
    course.credits = data["credits"]
    course.department = data["department"]

    db.session.commit()

    return jsonify(course.to_dict())


@app.route("/api/courses/<int:id>", methods=["DELETE"])
def delete_course(id):

    course = Course.query.get(id)

    if not course:
        return jsonify({
            "message": "Course not found"
        }), 404

    db.session.delete(course)

    db.session.commit()

    return jsonify({
        "message": "Course deleted successfully"
    })


if __name__ == "__main__":
    app.run(port=5001, debug=True)