import asyncio

from database import AsyncSessionLocal
from models import Department, Course, Student, Enrollment


async def seed():

    async with AsyncSessionLocal() as db:

        # Departments
        cs = Department(name="Computer Science")
        it = Department(name="Information Technology")

        db.add_all([cs, it])
        await db.commit()

        await db.refresh(cs)
        await db.refresh(it)

        # Courses
        c1 = Course(
            name="Python Programming",
            code="CS101",
            credits=4,
            department_id=cs.id
        )

        c2 = Course(
            name="FastAPI Development",
            code="CS102",
            credits=3,
            department_id=cs.id
        )

        c3 = Course(
            name="Database Systems",
            code="IT201",
            credits=4,
            department_id=it.id
        )

        db.add_all([c1, c2, c3])
        await db.commit()

        await db.refresh(c1)
        await db.refresh(c2)
        await db.refresh(c3)

        # Students
        s1 = Student(
            first_name="John",
            last_name="Doe",
            email="john@gmail.com",
            enrollment_year=2024,
            department_id=cs.id
        )

        s2 = Student(
            first_name="Alice",
            last_name="Smith",
            email="alice@gmail.com",
            enrollment_year=2023,
            department_id=cs.id
        )

        s3 = Student(
            first_name="Robert",
            last_name="Brown",
            email="robert@gmail.com",
            enrollment_year=2024,
            department_id=it.id
        )

        db.add_all([s1, s2, s3])
        await db.commit()

        await db.refresh(s1)
        await db.refresh(s2)
        await db.refresh(s3)

        # Enrollments
        e1 = Enrollment(
            student_id=s1.id,
            course_id=c1.id,
            semester="Semester 1",
            grade="A"
        )

        e2 = Enrollment(
            student_id=s2.id,
            course_id=c1.id,
            semester="Semester 1",
            grade="B+"
        )

        e3 = Enrollment(
            student_id=s2.id,
            course_id=c2.id,
            semester="Semester 2",
            grade="A"
        )

        e4 = Enrollment(
            student_id=s3.id,
            course_id=c3.id,
            semester="Semester 1",
            grade="A+"
        )

        db.add_all([e1, e2, e3, e4])

        await db.commit()

        print("Sample data inserted successfully!")


asyncio.run(seed())