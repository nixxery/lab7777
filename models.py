from sqlalchemy import Column, Integer, String
from database import db

class Books(db):
    __tablename__ = 'books'

    id = Column(Integer, primary_key=True, index=True)
    book_name = Column(String(50), index=True)
    author_name = Column(String(50), index=True)
    write_date = Column(Integer)
    janre = Column(String(50), index=True)

