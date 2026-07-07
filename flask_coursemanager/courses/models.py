from extensions import db


class Department(db.Model):
    __tablename__ = "departments"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)

    courses = db.relationship("Course", back_populates="department")
    students = db.relationship("Student", back_populates="department")

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name
        }


class Course(db.Model):
    __tablename__ = "courses"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    code = db.Column(db.String(20), unique=True, nullable=False)
    credits = db.Column(db.Integer, nullable=False)

    department_id = db.Column(
        db.Integer,
        db.ForeignKey("departments.id")
    )

    department = db.relationship(
        "Department",
        back_populates="courses"
    )

    enrollments = db.relationship(
        "Enrollment",
        back_populates="course"
    )

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "code": self.code,
            "credits": self.credits,
            "department_id": self.department_id
        }


class Student(db.Model):
    __tablename__ = "students"

    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50))
    last_name = db.Column(db.String(50))
    email = db.Column(db.String(100), unique=True)
    enrollment_year = db.Column(db.Integer)

    department_id = db.Column(
        db.Integer,
        db.ForeignKey("departments.id")
    )

    department = db.relationship(
        "Department",
        back_populates="students"
    )

    enrollments = db.relationship(
        "Enrollment",
        back_populates="student"
    )

    def to_dict(self):
        return {
            "id": self.id,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "email": self.email,
            "enrollment_year": self.enrollment_year,
            "department_id": self.department_id
        }


class Enrollment(db.Model):
    __tablename__ = "enrollments"

    id = db.Column(db.Integer, primary_key=True)

    student_id = db.Column(
        db.Integer,
        db.ForeignKey("students.id")
    )

    course_id = db.Column(
        db.Integer,
        db.ForeignKey("courses.id")
    )

    semester = db.Column(db.String(20))
    grade = db.Column(db.String(5))

    student = db.relationship(
        "Student",
        back_populates="enrollments"
    )

    course = db.relationship(
        "Course",
        back_populates="enrollments"
    )

    def to_dict(self):
        return {
            "id": self.id,
            "student_id": self.student_id,
            "course_id": self.course_id,
            "semester": self.semester,
            "grade": self.grade
        }