from sqlalchemy import Column, Integer, String
from .database import Base

class Book(Base):
    __tablename__ = "books"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    author = Column(String, nullable=False)

class Exam(Base):
    __tablename__ = "exams"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    code = Column(String, nullable=False)
    type = Column(String, nullable=False)
    year = Column(String, nullable=False)
    filename = Column(String, nullable=False)
    userid = Column(Integer, nullable=False)
