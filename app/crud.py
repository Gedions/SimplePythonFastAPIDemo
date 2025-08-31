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

def update_book(db: Session, book_id: int, book: schemas.BookCreate):
    db_book = db.query(models.Book).filter(models.Book.id == book_id).first()
    if db_book:
        db_book.title = book.title
        db_book.author = book.author
        db.commit()
        db.refresh(db_book)
    return db_book

def create_exam(db: Session, exam: schemas.ExamCreate):
    db_exam = models.Exam(**exam.dict())
    db.add(db_exam)
    db.commit()
    db.refresh(db_exam)
    return db_exam

def get_exams(db: Session, skip: int = 0, limit: int = 10):
    return db.query(models.Exam).offset(skip).limit(limit).all()
