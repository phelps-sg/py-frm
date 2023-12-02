# py-frm
This repo illustrates a proof-of-concept type-safe functional-relational mapping framework for Python inspired by [Slick](https://scala-slick.org/doc/stable/introduction.html).  The idea is that we can work with relational databases as if we are working with Python collections and dataclasses.  Moreover we can use [mypy](https://www.mypy-lang.org/) to provide type-safety.  

If you would like to see this project turned into a fully capable production-ready system, please star this repository and consider contributing by submitting issues and PRs.

## Illustrative end-user code

Our database model is represented using Python dataclasses, e.g.:

~~~python
from dataclasses import dataclass, field
from typing import ClassVar, Set

@dataclass
class Student:
    student_id: int = field(metadata={"primary_key": True})
    name: str

@dataclass
class Course:
    course_id: int = field(metadata={"primary_key": True})
    title: str
    student_id: int = field(metadata={"foreign_key": "students.student_id"})
~~~

Database queries are written as type-annotated Python generators using generator comprehensions:

~~~python
def get_student_courses(students: Iterable[Student], courses: Iterable[Course]) -> Generator:
    return ((s.name, c.title) for s in students for c in courses if s.student_id == c.student_id)
~~~

This type-annoted function can be statically checked by [mypy](https://www.mypy-lang.org/), and is automatically mapped onto the corresponding SQL query:

~~~sql
select name, title from students, courses where students.student_id = courses.student_id;
~~~
