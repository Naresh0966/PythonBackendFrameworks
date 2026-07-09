from typing import Optional

from fastapi import (
    FastAPI,
    Depends,
    HTTPException,
    Response,
    status
)

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database import engine, Base, get_db
from models import Course, Student, Enrollment
from schemas import CourseCreate, CourseUpdate, CourseResponse


app = FastAPI(
    title="Course Management API",
    description="FastAPI CRUD API for Course Management System",
    version="1.0",
    contact={
        "name": "Naresh",
        "email": "naresh@example.com"
    }
)


@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


@app.get("/")
async def root():
    return {"message": "API running"}


# -----------------------------
# CREATE COURSE
# -----------------------------
@app.post(
    "/api/courses/",
    response_model=CourseResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["Courses"],
    summary="Create a new course",
    response_description="Created course"
)
async def create_course(
    course: CourseCreate,
    db: AsyncSession = Depends(get_db)
):

    new_course = Course(
        name=course.name,
        code=course.code,
        credits=course.credits,
        department_id=course.department_id
    )

    db.add(new_course)

    await db.commit()
    await db.refresh(new_course)

    return new_course


# -----------------------------
# GET ALL COURSES
# -----------------------------
@app.get(
    "/api/courses/",
    response_model=list[CourseResponse], 
    tags=["Courses"],
    summary="Get all courses"
)
async def get_courses(
    skip: int = 0,
    limit: int = 10,
    department_id: Optional[int] = None,
    db: AsyncSession = Depends(get_db)
):

    query = select(Course)

    if department_id is not None:
        query = query.where(
            Course.department_id == department_id
        )

    query = query.offset(skip).limit(limit)

    result = await db.execute(query)

    courses = result.scalars().all()

    return courses


# -----------------------------
# GET COURSE BY ID
# -----------------------------
@app.get(
    "/api/courses/{course_id}",
    response_model=CourseResponse,
    tags=["Courses"],
    summary="Get course by ID"
)
async def get_course(
    course_id: int,
    db: AsyncSession = Depends(get_db)
):

    result = await db.execute(
        select(Course).where(Course.id == course_id)
    )

    course = result.scalar_one_or_none()

    if course is None:
        raise HTTPException(
            status_code=404,
            detail="Course not found"
        )

    return course


# -----------------------------
# UPDATE COURSE
# -----------------------------
@app.put(
    "/api/courses/{course_id}",
    response_model=CourseResponse,
    tags=["Courses"],
    summary="Update a course"
)
async def update_course(
    course_id: int,
    data: CourseUpdate,
    db: AsyncSession = Depends(get_db)
):

    result = await db.execute(
        select(Course).where(Course.id == course_id)
    )

    course = result.scalar_one_or_none()

    if course is None:
        raise HTTPException(
            status_code=404,
            detail="Course not found"
        )

    if data.name is not None:
        course.name = data.name

    if data.code is not None:
        course.code = data.code

    if data.credits is not None:
        course.credits = data.credits

    if data.department_id is not None:
        course.department_id = data.department_id

    await db.commit()
    await db.refresh(course)

    return course


# -----------------------------
# DELETE COURSE
# -----------------------------
@app.delete(
    "/api/courses/{course_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["Courses"],
    summary="Delete a course"
)
async def delete_course(
    course_id: int,
    db: AsyncSession = Depends(get_db)
):

    result = await db.execute(
        select(Course).where(Course.id == course_id)
    )

    course = result.scalar_one_or_none()

    if course is None:
        raise HTTPException(
            status_code=404,
            detail="Course not found"
        )

    await db.delete(course)
    await db.commit()

    return Response(status_code=status.HTTP_204_NO_CONTENT)


# -----------------------------
# GET STUDENTS OF A COURSE
# -----------------------------
@app.get(
    "/api/courses/{course_id}/students/",
    tags=["Courses"],
    summary="Get students enrolled in a course",
    response_description="List of enrolled students"
)
async def get_course_students(
    course_id: int,
    db: AsyncSession = Depends(get_db)
):

    result = await db.execute(
        select(Student)
        .join(Enrollment)
        .where(Enrollment.course_id == course_id)
    )

    students = result.scalars().all()

    if not students:
        raise HTTPException(
            status_code=404,
            detail="No students enrolled in this course"
        )

    return [student.to_dict() for student in students]
from models import Student
from schemas import StudentCreate, StudentUpdate, StudentResponse
@app.post(
    "/api/students/",
    response_model=StudentResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["Students"]
)
async def create_student(
    student: StudentCreate,
    db: AsyncSession = Depends(get_db)
):

    new_student = Student(
        first_name=student.first_name,
        last_name=student.last_name,
        email=student.email,
        enrollment_year=student.enrollment_year,
        department_id=student.department_id
    )

    db.add(new_student)
    await db.commit()
    await db.refresh(new_student)

    return new_student
@app.get(
    "/api/students/",
    response_model=list[StudentResponse],
    tags=["Students"]
)
async def get_students(
    db: AsyncSession = Depends(get_db)
):

    result = await db.execute(select(Student))
    return result.scalars().all()
@app.get(
    "/api/students/{student_id}",
    response_model=StudentResponse,
    tags=["Students"]
)
async def get_student(
    student_id: int,
    db: AsyncSession = Depends(get_db)
):

    result = await db.execute(
        select(Student).where(Student.id == student_id)
    )

    student = result.scalar_one_or_none()

    if student is None:
        raise HTTPException(404, "Student not found")

    return student
@app.put(
    "/api/students/{student_id}",
    response_model=StudentResponse,
    tags=["Students"]
)
async def update_student(
    student_id: int,
    data: StudentUpdate,
    db: AsyncSession = Depends(get_db)
):

    result = await db.execute(
        select(Student).where(Student.id == student_id)
    )

    student = result.scalar_one_or_none()

    if student is None:
        raise HTTPException(404, "Student not found")

    if data.first_name is not None:
        student.first_name = data.first_name

    if data.last_name is not None:
        student.last_name = data.last_name

    if data.email is not None:
        student.email = data.email

    if data.enrollment_year is not None:
        student.enrollment_year = data.enrollment_year

    if data.department_id is not None:
        student.department_id = data.department_id

    await db.commit()
    await db.refresh(student)

    return student
@app.delete(
    "/api/students/{student_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["Students"]
)
async def delete_student(
    student_id: int,
    db: AsyncSession = Depends(get_db)
):

    result = await db.execute(
        select(Student).where(Student.id == student_id)
    )

    student = result.scalar_one_or_none()

    if student is None:
        raise HTTPException(404, "Student not found")

    await db.delete(student)
    await db.commit()

    return Response(status_code=204)
from fastapi import BackgroundTasks
from schemas import EnrollmentCreate, EnrollmentResponse
def send_confirmation_email(student_email: str):
    print(f"Sending confirmation to {student_email}")
@app.post(
    "/api/enrollments/",
    response_model=EnrollmentResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["Enrollments"]
)
async def create_enrollment(
    enrollment: EnrollmentCreate,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):

    student = await db.get(Student, enrollment.student_id)

    if student is None:
        raise HTTPException(404, "Student not found")

    course = await db.get(Course, enrollment.course_id)

    if course is None:
        raise HTTPException(404, "Course not found")

    new_enrollment = Enrollment(
        student_id=enrollment.student_id,
        course_id=enrollment.course_id,
        semester=enrollment.semester,
        grade=enrollment.grade
    )

    db.add(new_enrollment)

    await db.commit()
    await db.refresh(new_enrollment)

    background_tasks.add_task(
        send_confirmation_email,
        student.email
    )

    return new_enrollment
@app.get(
    "/api/enrollments/",
    response_model=list[EnrollmentResponse],
    tags=["Enrollments"]
)
async def get_enrollments(
    db: AsyncSession = Depends(get_db)
):

    result = await db.execute(select(Enrollment))

    return result.scalars().all()
@app.delete(
    "/api/enrollments/{enrollment_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["Enrollments"]
)
async def delete_enrollment(
    enrollment_id: int,
    db: AsyncSession = Depends(get_db)
):

    enrollment = await db.get(
        Enrollment,
        enrollment_id
    )

    if enrollment is None:
        raise HTTPException(404, "Enrollment not found")

    await db.delete(enrollment)

    await db.commit()

    return Response(status_code=204)
