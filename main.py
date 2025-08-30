from typing import List, Optional

from fastapi import FastAPI, Depends, HTTPException, UploadFile, File, Form
import os
import shutil
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from pydantic import BaseModel, ConfigDict

from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import declarative_base, sessionmaker, Session

# ---------------------------
# 1) DATABASE CONFIG (SQLite)
# ---------------------------
SQLALCHEMY_DATABASE_URL = "sqlite:///./app.db"  # file will appear in project folder
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},  # needed for SQLite + threads
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


# ---------------------------
# 2) DB MODEL (a table)
# ---------------------------
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


class ExamCreate(BaseModel):
    title: str
    code: str
    type: str
    year: str
    filename: str
    userid: int


# Create tables if they don't exist yet
Base.metadata.create_all(bind=engine)


# ---------------------------
# 3) FASTAPI APP
# ---------------------------
app = FastAPI(title="FastAPI + SQLite (Books)")


# Serve files from /static at /static/*
app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")

# Return index.html at the homepage
@app.get("/", include_in_schema=False)
def serve_index():
    return FileResponse("static/index.html")


# ---------------------------
# 4) SCHEMAS (request/response shapes)
# ---------------------------
class BookCreate(BaseModel):
    title: str
    author: str


class BookRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)  # Pydantic v2: read from ORM
    id: int
    title: str
    author: str


class BookUpdate(BaseModel):
    title: Optional[str] = None
    author: Optional[str] = None


class ExamRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    title: str
    code: str
    type: str
    year: str
    filename: str
    userid: int


# ---------------------------
# 5) DB SESSION DEPENDENCY
# ---------------------------
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ---------------------------
# 6) CRUD ROUTES (JSON API)
# ---------------------------
@app.post("/api/books", response_model=BookRead)
def create_book(book: BookCreate, db: Session = Depends(get_db)):
    db_book = Book(title=book.title, author=book.author)
    db.add(db_book)
    db.commit()
    db.refresh(db_book)
    return db_book


@app.post("/api/exams", response_model=ExamRead)
def create_exam(
    title: str = Form(...),
    code: str = Form(...),
    type: str = Form(...),
    year: str = Form(...),
    userid: int = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    # Save file
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Create exam record
    exam = Exam(
        title=title,
        code=code,
        type=type,
        year=year,
        filename=file.filename,
        userid=userid
    )
    db.add(exam)
    db.commit()
    db.refresh(exam)
    return exam


@app.get("/api/exams", response_model=List[ExamRead])
def list_exams(db: Session = Depends(get_db)):
    return db.query(Exam).all()


@app.get("/api/books", response_model=List[BookRead])
def list_books(db: Session = Depends(get_db)):
    return db.query(Book).all()


@app.get("/api/books/{book_id}", response_model=BookRead)
def get_book(book_id: int, db: Session = Depends(get_db)):
    db_book = db.get(Book, book_id)
    if not db_book:
        raise HTTPException(status_code=404, detail="Book not found")
    return db_book


@app.put("/api/books/{book_id}", response_model=BookRead)
def update_book(book_id: int, book: BookUpdate, db: Session = Depends(get_db)):
    db_book = db.get(Book, book_id)
    if not db_book:
        raise HTTPException(status_code=404, detail="Book not found")
    if book.title is not None:
        db_book.title = book.title
    if book.author is not None:
        db_book.author = book.author
    db.commit()
    db.refresh(db_book)
    return db_book


@app.delete("/api/books/{book_id}")
def delete_book(book_id: int, db: Session = Depends(get_db)):
    db_book = db.get(Book, book_id)
    if not db_book:
        raise HTTPException(status_code=404, detail="Book not found")
    db.delete(db_book)
    db.commit()
    return {"message": "Book deleted"}

@app.post("/api/upload/")
def upload_file(file: UploadFile = File(...)):
    file_location = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_location, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    return {"filename": file.filename, "message": "File uploaded successfully"}

@app.get("/api/files/{filename}")
def get_file(filename: str):
    file_location = os.path.join(UPLOAD_DIR, filename)
    if not os.path.exists(file_location):
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(file_location)

@app.get("/api/files/")
def list_files():
    files = os.listdir(UPLOAD_DIR)
    return {"files": files}
