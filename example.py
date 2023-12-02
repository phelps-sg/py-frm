from dataclasses import dataclass, field
from typing import Iterable, Generator

from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import sessionmaker

from py_frm import Base, sqlalchemy_model, to_sqlalchemy_query, model_for


@sqlalchemy_model(table="students")
@dataclass
class Student:
    student_id: int = field(metadata={"primary_key": True})
    name: str


@sqlalchemy_model(table="courses")
@dataclass
class Course:
    course_id: int = field(metadata={"primary_key": True})
    title: str
    student_id: int = field(metadata={"foreign_key": ("students", "student_id")})


def get_student_courses(
    students: Iterable[Student], courses: Iterable[Course]
) -> Generator:
    return (
        (s.name, c.title)
        for s in students
        for c in courses
        if s.student_id == c.student_id
    )


def populate_db(session):
    StudentModel = model_for("students")
    CourseModel = model_for("courses")

    students = [
        StudentModel(student_id=1, name="Alice"),
        StudentModel(student_id=2, name="Bob"),
        StudentModel(student_id=3, name="Charlie"),
    ]
    session.add_all(students)

    courses = [
        CourseModel(course_id=1, title="Mathematics", student_id=1),
        CourseModel(course_id=2, title="Physics", student_id=2),
        CourseModel(course_id=3, title="Chemistry", student_id=1),
    ]
    session.add_all(courses)

    session.commit()


def main():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    inspector = inspect(engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    tables = inspector.get_table_names()
    print("Tables in the database:", tables)

    populate_db(session)

    query = to_sqlalchemy_query(get_student_courses, session)
    print(f"SQL: {query.statement}")
    for result in query.all():
        print(result)


if __name__ == "__main__":
    main()
