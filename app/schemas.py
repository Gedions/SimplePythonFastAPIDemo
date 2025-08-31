from pydantic import BaseModel

class BookCreate(BaseModel):
    title: str
    author: str

class BookOut(BookCreate):
    id: int
    class Config:
        orm_mode = True

class ExamCreate(BaseModel):
    title: str
    code: str
    type: str
    year: str
    filename: str
    userid: int

class ExamOut(ExamCreate):
    id: int
    class Config:
        orm_mode = True
