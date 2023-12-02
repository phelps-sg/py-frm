from dataclasses import dataclass, field
from typing import Iterable, Generator

from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import sessionmaker

from py_frm import sqlalchemy_model
from py_frm.compiler import to_sqlalchemy_query
from py_frm.model import Base


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


if __name__ == "__main__":
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    inspector = inspect(engine)

    tables = inspector.get_table_names()
    print("Tables in the database:", tables)

    Session = sessionmaker(bind=engine)
    session = Session()
    query = to_sqlalchemy_query(get_student_courses, session)
    for result in query.all():
        print(result)
