from typing import Optional
from security import *

from models import User
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from jose import JWTError
from fastapi import (
    FastAPI,
    Depends,
    HTTPException,
    status,
    Response,
    Request,
    BackgroundTasks
)
import sqlalchemy.ext.asyncio
from sqlalchemy import select, func, or_
from database import engine, Base, get_db
from models import Course, Student, Enrollment
from schemas import *

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


def error_response(code, message, field=None):
    raise HTTPException(
        status_code=404,
        detail={
            "error": {
                "code": code,
                "message": message,
                "field": field
            }
        }
    )


@app.get("/")
async def root():
    return {
        "message": "Course Management API Running"
    }
# ------------------------------------
# AUTHENTICATION
# ------------------------------------

@app.post(
    "/api/v1/auth/register/",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["Authentication"],
    summary="Register a new user"
)
async def register_user(
    user: UserRegister,
    db: sqlalchemy.ext.asyncio.AsyncSession = Depends(get_db)
):

    # Check if email already exists
    result = await db.execute(
        select(User).where(User.email == user.email)
    )

    existing_user = result.scalar_one_or_none()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered"
        )

    # Never store plain-text passwords.
    # bcrypt is preferred over MD5/SHA256 because
    # it is intentionally slow and resistant to brute-force attacks.

    hashed_password = get_password_hash(user.password)

    new_user = User(
        email=user.email,
        hashed_password=hashed_password,
        is_active=True
    )

    db.add(new_user)

    await db.commit()

    await db.refresh(new_user)

    return new_user

# ------------------------------------
# COURSES
# ------------------------------------

@app.get(
    "/api/v1/courses/",
    tags=["Courses"],
    summary="Get all courses"
)
async def get_courses(
    request: Request,
    page: int = 1,
    page_size: int = 5,
    search: Optional[str] = None,
    department_id: Optional[int] = None,
    db: sqlalchemy.ext.asyncio.AsyncSession = Depends(get_db)
):

    query = select(Course)

    if search:

        query = query.where(
            or_(
                Course.name.ilike(f"%{search}%"),
                Course.code.ilike(f"%{search}%")
            )
        )

    if department_id:

        query = query.where(
            Course.department_id == department_id
        )

    total = await db.execute(
        select(func.count()).select_from(query.subquery())
    )

    count = total.scalar()

    offset = (page - 1) * page_size

    result = await db.execute(
        query.offset(offset).limit(page_size)
    )

    courses = result.scalars().all()

    next_page = None

    if offset + page_size < count:
        next_page = (
            f"/api/v1/courses/?page={page+1}&page_size={page_size}"
        )

    previous_page = None

    if page > 1:
        previous_page = (
            f"/api/v1/courses/?page={page-1}&page_size={page_size}"
        )

    return {

        "count": count,

        "next": next_page,

        "previous": previous_page,

        "results": [
            course.to_dict()
            for course in courses
        ]
    }


@app.get(
    "/api/v1/courses/{course_id}",
    response_model=CourseResponse,
    tags=["Courses"]
)
async def get_course(
    course_id: int,
    db: sqlalchemy.ext.asyncio.AsyncSession = Depends(get_db)
):

    result = await db.execute(
        select(Course)
        .where(Course.id == course_id)
    )

    course = result.scalar_one_or_none()

    if course is None:

        error_response(
            "NOT_FOUND",
            f"Course with id {course_id} does not exist"
        )

    return course
# ------------------------------------
# CREATE COURSE
# ------------------------------------

@app.post(
    "/api/v1/courses/",
    response_model=CourseResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["Courses"],
    summary="Create a new course",
    response_description="New course created successfully"
)
async def create_course(
    response: Response,
    course: CourseCreate,
    db: sqlalchemy.ext.asyncio.AsyncSession = Depends(get_db)
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

    response.headers["Location"] = f"/api/v1/courses/{new_course.id}"

    return new_course


# ------------------------------------
# PUT (Replace Entire Course)
# ------------------------------------

@app.put(
    "/api/v1/courses/{course_id}",
    response_model=CourseResponse,
    tags=["Courses"],
    summary="Replace a course"
)
async def update_course(
    course_id: int,
    data: CourseCreate,
    db: sqlalchemy.ext.asyncio.AsyncSession = Depends(get_db)
):

    result = await db.execute(
        select(Course).where(Course.id == course_id)
    )

    course = result.scalar_one_or_none()

    if course is None:

        error_response(
            "NOT_FOUND",
            f"Course with id {course_id} does not exist"
        )

    course.name = data.name
    course.code = data.code
    course.credits = data.credits
    course.department_id = data.department_id

    await db.commit()

    await db.refresh(course)

    return course


# ------------------------------------
# PATCH (Partial Update)
# ------------------------------------

@app.patch(
    "/api/v1/courses/{course_id}",
    response_model=CourseResponse,
    tags=["Courses"],
    summary="Partially update a course"
)
async def patch_course(
    course_id: int,
    data: CourseUpdate,
    db: sqlalchemy.ext.asyncio.AsyncSession = Depends(get_db)
):

    result = await db.execute(
        select(Course).where(Course.id == course_id)
    )

    course = result.scalar_one_or_none()

    if course is None:

        error_response(
            "NOT_FOUND",
            f"Course with id {course_id} does not exist"
        )

    update_data = data.model_dump(exclude_unset=True)

    for key, value in update_data.items():
        setattr(course, key, value)

    await db.commit()

    await db.refresh(course)

    return course


# ------------------------------------
# DELETE COURSE
# ------------------------------------

@app.delete(
    "/api/v1/courses/{course_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["Courses"],
    summary="Delete a course"
)
async def delete_course(
    course_id: int,
    db: sqlalchemy.ext.asyncio.AsyncSession = Depends(get_db)
):

    result = await db.execute(
        select(Course).where(Course.id == course_id)
    )

    course = result.scalar_one_or_none()

    if course is None:

        error_response(
            "NOT_FOUND",
            f"Course with id {course_id} does not exist"
        )

    await db.delete(course)

    await db.commit()

    return Response(
        status_code=status.HTTP_204_NO_CONTENT
    )


# ------------------------------------
# COURSE STUDENTS (JOIN)
# ------------------------------------

@app.get(
    "/api/v1/courses/{course_id}/students/",
    tags=["Courses"],
    summary="Students enrolled in a course"
)
async def get_course_students(
    course_id: int,
    db: sqlalchemy.ext.asyncio.AsyncSession = Depends(get_db)
):

    result = await db.execute(

        select(Student)

        .join(Enrollment)

        .where(
            Enrollment.course_id == course_id
        )
    )

    students = result.scalars().all()

    return [
        student.to_dict()
        for student in students
    ]
# ------------------------------------
# STUDENTS
# ------------------------------------

@app.get(
    "/api/v1/students/",
    response_model=list[StudentResponse],
    tags=["Students"],
    summary="Get all students"
)
async def get_students(
    db: sqlalchemy.ext.asyncio.AsyncSession = Depends(get_db)
):

    result = await db.execute(select(Student))

    return result.scalars().all()


@app.post(
    "/api/v1/students/",
    response_model=StudentResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["Students"],
    summary="Create a student"
)
async def create_student(
    response: Response,
    student: StudentCreate,
    db: sqlalchemy.ext.asyncio.AsyncSession = Depends(get_db)
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

    response.headers["Location"] = (
        f"/api/v1/students/{new_student.id}"
    )

    return new_student


@app.put(
    "/api/v1/students/{student_id}",
    response_model=StudentResponse,
    tags=["Students"]
)
async def update_student(
    student_id: int,
    student: StudentCreate,
    db: sqlalchemy.ext.asyncio.AsyncSession = Depends(get_db)
):

    result = await db.execute(
        select(Student).where(Student.id == student_id)
    )

    existing = result.scalar_one_or_none()

    if existing is None:
        error_response(
            "NOT_FOUND",
            f"Student with id {student_id} does not exist"
        )

    existing.first_name = student.first_name
    existing.last_name = student.last_name
    existing.email = student.email
    existing.enrollment_year = student.enrollment_year
    existing.department_id = student.department_id

    await db.commit()

    await db.refresh(existing)

    return existing


@app.delete(
    "/api/v1/students/{student_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["Students"]
)
async def delete_student(
    student_id: int,
    db: sqlalchemy.ext.asyncio.AsyncSession = Depends(get_db)
):

    result = await db.execute(
        select(Student).where(Student.id == student_id)
    )

    student = result.scalar_one_or_none()

    if student is None:
        error_response(
            "NOT_FOUND",
            f"Student with id {student_id} does not exist"
        )

    await db.delete(student)

    await db.commit()

    return Response(
        status_code=status.HTTP_204_NO_CONTENT
    )


# ------------------------------------
# BACKGROUND TASK
# ------------------------------------

def send_confirmation_email(email: str):

    print(f"Sending confirmation email to {email}")


# ------------------------------------
# ENROLLMENTS
# ------------------------------------

@app.get(
    "/api/v1/enrollments/",
    tags=["Enrollments"],
    summary="Get all enrollments"
)
async def get_enrollments(
    db: sqlalchemy.ext.asyncio.AsyncSession = Depends(get_db)
):

    result = await db.execute(
        select(Enrollment)
    )

    enrollments = result.scalars().all()

    return [

        {
            "id": e.id,
            "student_id": e.student_id,
            "course_id": e.course_id,
            "semester": e.semester,
            "grade": e.grade
        }

        for e in enrollments
    ]


@app.post(
    "/api/v1/enrollments/",
    status_code=status.HTTP_201_CREATED,
    tags=["Enrollments"],
    summary="Enroll student into course"
)
async def create_enrollment(

    enrollment: EnrollmentCreate,

    background_tasks: BackgroundTasks,

    db: sqlalchemy.ext.asyncio.AsyncSession = Depends(get_db)
):

    student_result = await db.execute(
        select(Student).where(
            Student.id == enrollment.student_id
        )
    )

    student = student_result.scalar_one_or_none()

    if student is None:

        error_response(
            "NOT_FOUND",
            "Student not found"
        )

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

    return {

        "message": "Enrollment created successfully",

        "enrollment": {

            "id": new_enrollment.id,

            "student_id": new_enrollment.student_id,

            "course_id": new_enrollment.course_id,

            "semester": new_enrollment.semester,

            "grade": new_enrollment.grade
        }
    }


@app.delete(
    "/api/v1/enrollments/{enrollment_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["Enrollments"]
)
async def delete_enrollment(
    enrollment_id: int,
    db: sqlalchemy.ext.asyncio.AsyncSession = Depends(get_db)
):

    result = await db.execute(
        select(Enrollment).where(
            Enrollment.id == enrollment_id
        )
    )

    enrollment = result.scalar_one_or_none()

    if enrollment is None:

        error_response(
            "NOT_FOUND",
            f"Enrollment with id {enrollment_id} does not exist"
        )

    await db.delete(enrollment)

    await db.commit()

    return Response(
        status_code=status.HTTP_204_NO_CONTENT
    )
@app.post(
    "/api/v1/auth/login/",
    response_model=Token,
    tags=["Authentication"],
    summary="Login"
)
async def login(

    form_data: OAuth2PasswordRequestForm = Depends(),

    db: sqlalchemy.ext.asyncio.AsyncSession = Depends(get_db)

):

    result = await db.execute(

        select(User)

        .where(User.email == form_data.username)

    )

    user = result.scalar_one_or_none()

    if user is None:

        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )

    if not verify_password(
        form_data.password,
        user.hashed_password
    ):

        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )

    token = create_access_token(
        {
            "sub": user.email
        }
    )

    return {

        "access_token": token,

        "token_type": "bearer"

    }
async def get_current_user(

    token: str = Depends(oauth2_scheme),

    db: sqlalchemy.ext.asyncio.AsyncSession = Depends(get_db)

):

    payload = decode_access_token(token)

    if payload is None:

        raise HTTPException(
            status_code=401,
            detail="Invalid or expired token"
        )

    email = payload.get("sub")

    result = await db.execute(

        select(User)

        .where(User.email == email)

    )

    user = result.scalar_one_or_none()

    if user is None:

        raise HTTPException(
            status_code=401,
            detail="User not found"
        )

    return user
async def create_course(

    response: Response,

    course: CourseCreate,

    current_user: User = Depends(get_current_user),

    db: sqlalchemy.ext.asyncio.AsyncSession = Depends(get_db)

):
    # create a new course owned by the current user
    new_course = Course(**course.dict(), owner_id=current_user.id)
    db.add(new_course)
    await db.commit()
    await db.refresh(new_course)
    response.status_code = 201
    return new_course