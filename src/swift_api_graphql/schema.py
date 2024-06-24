from datetime import date
from typing import List, Optional

from sqlalchemy.orm import Session

import strawberry
from strawberry.types import Info

from .models import BookModel

@strawberry.type
class Book:
    id: int
    title: str
    author: str
    date_published: date
    cover_image: str

@strawberry.input
class BookInput:
    title: str
    author: str
    date_published: date
    cover_image: str

@strawberry.type
class Query:
    @strawberry.field
    def books(self, info: Info) -> List[Book]:
        db: Session = info.context["db"]
        return db.query(BookModel).all()

    @strawberry.field
    def book(self, info: Info, id: int) -> Optional[Book]:
        db: Session = info.context["db"]
        return db.query(BookModel).filter(BookModel.id == id).first()

@strawberry.type
class Mutation:
    @strawberry.mutation
    def create_book(self, info: Info, book: BookInput) -> Book:
        db: Session = info.context["db"]
        db_book = BookModel(**book.__dict__)
        db.add(db_book)
        db.commit()
        db.refresh(db_book)
        return db_book

    @strawberry.mutation
    def update_book(self, info: Info, id: int, book: BookInput) -> Optional[Book]:
        db: Session = info.context["db"]
        db_book = db.query(BookModel).filter(BookModel.id == id).first()
        if db_book:
            for key, value in book.__dict__.items():
                setattr(db_book, key, value)
            db.commit()
            db.refresh(db_book)
        return db_book

    @strawberry.mutation
    def delete_book(self, info: Info, id: int) -> bool:
        db: Session = info.context["db"]
        db_book = db.query(BookModel).filter(BookModel.id == id).first()
        if db_book:
            db.delete(db_book)
            db.commit()
            return True
        return False

schema = strawberry.Schema(query=Query, mutation=Mutation)
