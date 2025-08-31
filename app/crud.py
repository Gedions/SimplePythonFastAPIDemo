from sqlalchemy.orm import Session
from . import models, schemas

def create_book(db: Session, book: schemas.BookCreate):
    db_book = models.Book(title=book.title, author=book.author)
    db.add(db_book)
    db.commit()
    db.refresh(db_book)
    return db_book

def get_books(db: Session):
    return db.query(models.Book).all()

def create_exam(db: Session, exam: schemas.ExamCreate):
    db_exam = models.Exam(**exam.dict())
    db.add(db_exam)
    db.commit()
    db.refresh(db_exam)
    return db_exam

def get_exams(db: Session):
    return db.query(models.Exam).all()
