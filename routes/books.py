from fastapi import Depends, HTTPException, APIRouter, Query
from sqlmodel import Session, select
from database import get_session
from models.book import Book, BookCreate, BookRead, BookUpdate

from auth import verify_api_key
from models.user import User
from typing import Optional
router = APIRouter(prefix="/books", tags=["books"])

@router.get("/", response_model=list[BookRead])
def list_books(
    title: Optional[str] = Query(default=None),
    author: Optional[str] = Query(default=None),
    session: Session = Depends(get_session)
):
    query = select(Book).where(
        Book.is_sold == False  # Only fetch unsold books
    )
    if title:
        query = query.where(Book.title.contains(title))
    if author:
        query = query.where(Book.author.contains(author))

    books = session.exec(query).all()
    return books


@router.post("/",response_model=BookRead)
def create_book(
    book_date: BookCreate,
    session: Session = Depends(get_session),
    api_key: str = Depends(verify_api_key)
):
    book = Book.model_validate(book_date)
    session.add(book)
    session.commit()
    session.refresh(book)
    return book

@router.patch("/{book_id}/sell", response_model=BookRead)
def update_book(
    book_id: int,
    updates: BookUpdate,
    session: Session = Depends(get_session),
    api_key: str = Depends(verify_api_key)
):
    book = session.get(Book, book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")

    book_data = updates.model_dump(exclude_unset=True)
    for key, value in book_data.items():
        setattr(book, key, value)
    session.add(book)
    session.commit()
    session.refresh(book)
    return book

@router.patch("/{book_id}/sold", response_model=BookRead)
def mark_book_as_sold(
    book_id: int,
    session: Session = Depends(get_session),
    api_key: str = Depends(verify_api_key)
):
    book = session.get(Book, book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")

    book.is_sold = True
    session.add(book)
    session.commit()
    session.refresh(book)
    return book