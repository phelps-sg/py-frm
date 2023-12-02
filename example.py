from dataclasses import dataclass, field

from sqlalchemy import create_engine, inspect

from py_frm import sqlalchemy_model
from py_frm.model import Base


@sqlalchemy_model
@dataclass
class Student:
    student_id: int = field(metadata={"primary_key": True})
    name: str


@sqlalchemy_model
@dataclass
class Course:
    course_id: int = field(metadata={"primary_key": True})
    title: str
    student_id: int = field(metadata={"foreign_key": ("students", "student_id")})


if __name__ == "__main__":
    engine = create_engine('sqlite:///:memory:')
    Base.metadata.create_all(engine)
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    print("Tables in the database:", tables)
