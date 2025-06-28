from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import Column, Integer, String, Boolean, Sequence

class Base(DeclarativeBase):
    pass

    @classmethod
    def generate_id(cls, name):
        return Sequence(f'{name}_id_seq', metadata=cls.metadata)
