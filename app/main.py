from fastapi import FastAPI, Depends, Form, UploadFile
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os
from sqlalchemy.orm import Session
from . import models, schemas, crud
from .database import engine, SessionLocal, Base

app = FastAPI(title="Books and Exams API")

# Serve the "static" folder (css/js/images)
app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# Dependency for DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Serve your index.html at the root "/"
@app.get("/")
async def read_index():
    return FileResponse(os.path.join("static", "index.html"))

@app.post("/api/books/", response_model=schemas.BookOut)
def add_book(title: str = Form(...), 
             author: str = Form(...), 
             db: Session = Depends(get_db)):
    book = schemas.BookCreate(title=title, author=author)
    return crud.create_book(db, book)

@app.get("/api/books/", response_model=list[schemas.BookOut])
def read_books(db: Session = Depends(get_db)):
    return crud.get_books(db)

@app.post("/api/exams/", response_model=schemas.ExamOut)
async def add_exam(
    title: str = Form(...),
    code: str = Form(...),
    type: str = Form(...),
    year: str = Form(...),
    filename: UploadFile = Form(...),
    userid: int = Form(...),
    db: Session = Depends(get_db)
):
    uploads_dir = "uploads"
    os.makedirs(uploads_dir, exist_ok=True)
    file_location = os.path.join(uploads_dir, filename.filename)

    with open(file_location, "wb") as f:
        f.write(await filename.read())
        
    exam = schemas.ExamCreate(
        title=title, code=code, type=type, year=year, filename=file_location, userid=userid
    )
    
    return crud.create_exam(db, exam)

@app.get("/api/exams/", response_model=list[schemas.ExamOut])
def read_exams(db: Session = Depends(get_db)):
    return crud.get_exams(db)

@app.get("/api/exams/{exam_id}", response_model=schemas.ExamOut)
def read_exam(exam_id: int, db: Session = Depends(get_db)):
    exam = crud.get_exam(db, exam_id)
    if exam is None:
        return {"error": "Exam not found"}
    return exam

@app.put("/api/books/{book_id}", response_model=schemas.BookOut)
def update_book(
    book_id: int,
    title: str = Form(...),
    author: str = Form(...),
    db: Session = Depends(get_db)
):
    book = schemas.BookCreate(title=title, author=author)
    return crud.update_book(db, book_id, book)

@app.delete("/api/books/{book_id}", response_model=schemas.BookOut)
def delete_book(book_id: int, db: Session = Depends(get_db)):
    return crud.delete_book(db, book_id)

@app.put("/api/exams/{exam_id}", response_model=schemas.ExamOut)
def update_exam(
    exam_id: int,
    title: str = Form(...),
    code: str = Form(...),
    type: str = Form(...),
    year: str = Form(...),
    filename: UploadFile = Form(None),
    db: Session = Depends(get_db)
):
    if filename:
        uploads_dir = "uploads"
        os.makedirs(uploads_dir, exist_ok=True)
        file_location = os.path.join(uploads_dir, filename.filename)

        with open(file_location, "wb") as f:
            f.write(filename.file.read())
    else:
        file_location = None
    exam = schemas.ExamCreate(
        title=title, code=code, type=type, year=year, filename=file_location
    )
    
    return crud.update_exam(db, exam_id, exam)

@app.delete("/api/exams/{exam_id}", response_model=schemas.ExamOut)
def delete_exam(exam_id: int, db: Session = Depends(get_db)):
    exam = crud.get_exam(db, exam_id)
    if exam and exam.filename:
        try:
            os.remove(exam.filename)
        except FileNotFoundError:
            pass
    return crud.delete_exam(db, exam_id)