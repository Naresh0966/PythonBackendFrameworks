from typing import Optional, List
from pydantic import BaseModel, ConfigDict


# ----------------------------
# COURSE SCHEMAS
# ----------------------------

class CourseCreate(BaseModel):
    name: str
    code: str
    credits: int
    department_id: int


class CourseUpdate(BaseModel):
    name: Optional[str] = None
    code: Optional[str] = None
    credits: Optional[int] = None
    department_id: Optional[int] = None


class CourseResponse(BaseModel):
    id: int
    name: str
    code: str
    credits: int
    department_id: int

    model_config = ConfigDict(from_attributes=True)


# ----------------------------
# STUDENT SCHEMAS
# ----------------------------

class StudentCreate(BaseModel):
    first_name: str
    last_name: str
    email: str
    enrollment_year: int
    department_id: int


class StudentUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[str] = None
    enrollment_year: Optional[int] = None
    department_id: Optional[int] = None


class StudentResponse(BaseModel):
    id: int
    first_name: str
    last_name: str
    email: str
    enrollment_year: int
    department_id: int

    model_config = ConfigDict(from_attributes=True)


# ----------------------------
# ENROLLMENT SCHEMAS
# ----------------------------

class EnrollmentCreate(BaseModel):
    student_id: int
    course_id: int
    semester: str
    grade: str


class EnrollmentUpdate(BaseModel):
    semester: Optional[str] = None
    grade: Optional[str] = None


class EnrollmentResponse(BaseModel):
    id: int
    student_id: int
    course_id: int
    semester: str
    grade: str

    model_config = ConfigDict(from_attributes=True)


# ----------------------------
# DEPARTMENT SCHEMA
# ----------------------------

class DepartmentResponse(BaseModel):
    id: int
    name: str
    courses: List[CourseResponse] = []

    model_config = ConfigDict(from_attributes=True)

from pydantic import EmailStr

class UserRegister(BaseModel):

    email: EmailStr

    password: str


class UserLogin(BaseModel):

    email: EmailStr

    password: str


class UserResponse(BaseModel):

    id: int

    email: EmailStr

    is_active: bool

    model_config = ConfigDict(
        from_attributes=True
    )


class Token(BaseModel):

    access_token: str

    token_type: str
