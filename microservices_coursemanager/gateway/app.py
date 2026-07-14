from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

COURSE_SERVICE = "http://127.0.0.1:5001"
STUDENT_SERVICE = "http://127.0.0.1:5002"


@app.route("/")
def home():

    return jsonify({
        "Gateway": "Running"
    })


@app.route("/api/courses", methods=["GET", "POST"])
def courses():

    response = requests.request(
        method=request.method,
        url=f"{COURSE_SERVICE}/api/courses",
        json=request.get_json(silent=True)
    )

    return (
        response.content,
        response.status_code,
        response.headers.items()
    )


@app.route("/api/courses/<path:path>", methods=["GET", "PUT", "DELETE"])
def course_by_id(path):

    response = requests.request(
        method=request.method,
        url=f"{COURSE_SERVICE}/api/courses/{path}",
        json=request.get_json(silent=True)
    )

    return (
        response.content,
        response.status_code,
        response.headers.items()
    )


@app.route("/api/students", methods=["GET", "POST"])
def students():

    response = requests.request(
        method=request.method,
        url=f"{STUDENT_SERVICE}/api/students",
        json=request.get_json(silent=True)
    )

    return (
        response.content,
        response.status_code,
        response.headers.items()
    )


@app.route(
    "/api/students/<path:path>",
    methods=["GET", "PUT", "DELETE", "POST"]
)
def student(path):

    response = requests.request(
        method=request.method,
        url=f"{STUDENT_SERVICE}/api/students/{path}",
        json=request.get_json(silent=True)
    )

    return (
        response.content,
        response.status_code,
        response.headers.items()
    )


if __name__ == "__main__":
    app.run(port=5000, debug=True)