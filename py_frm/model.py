from dataclasses import fields

from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
models = dict()


def create_sqlalchemy_model(dataclass):
    attributes = {"__tablename__": dataclass.__name__.lower() + "s"}

    for field in fields(dataclass):  # Correctly access fields
        field_type = field.type
        primary_key = field.metadata.get("primary_key", False)
        foreign_key = field.metadata.get("foreign_key", None)

        if field_type == int:
            column_type = Integer
        elif field_type == str:
            column_type = String
        else:
            raise TypeError(f"Unsupported type: {field_type}")

        if foreign_key:
            table, ref_column = foreign_key
            attributes[field.name] = Column(
                column_type,
                ForeignKey(f"{table}.{ref_column}"),
                primary_key=primary_key,
            )
        else:
            attributes[field.name] = Column(column_type, primary_key=primary_key)

    return type(dataclass.__name__ + "Model", (Base,), attributes)


def sqlalchemy_model(table):
    def decorator(dataclass):
        def wrapper(cls):
            model = create_sqlalchemy_model(cls)
            models[table] = model

        return wrapper(dataclass)
    return decorator
