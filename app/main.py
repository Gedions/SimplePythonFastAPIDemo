from fastapi import FastAPI, Depends, Form
from sqlalchemy.orm import Session
from . import models, schemas, crud
from .database import engine, SessionLocal, Base

app = FastAPI(title="Books and Exams API")

# Dependency for DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/books/", response_model=schemas.BookOut)
def add_book(title: str = Form(...), author: str = Form(...), db: Session = Depends(get_db)):
    book = schemas.BookCreate(title=title, author=author)
    return crud.create_book(db, book)

@app.get("/books/", response_model=list[schemas.BookOut])
def read_books(db: Session = Depends(get_db)):
    return crud.get_books(db)

@app.post("/exams/", response_model=schemas.ExamOut)
def add_exam(
    title: str = Form(...),
    code: str = Form(...),
    type: str = Form(...),
    year: str = Form(...),
    filename: str = Form(...),
    userid: int = Form(...),
    db: Session = Depends(get_db)
):
    exam = schemas.ExamCreate(
        title=title, code=code, type=type, year=year, filename=filename, userid=userid
    )
    return crud.create_exam(db, exam)

@app.get("/exams/", response_model=list[schemas.ExamOut])
def read_exams(db: Session = Depends(get_db)):
    return crud.get_exams(db)
