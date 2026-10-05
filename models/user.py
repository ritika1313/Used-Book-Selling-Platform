from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from models.book import Book  # Avoid circular import issues

class UserCreate(SQLModel):
    name: str
    email: str
    college: str


class UserRead(SQLModel):
    id: int
    name: str
    email: str
    college: str


class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    email: str = Field(unique=True)
    college: str

    books: list["Book"] = Relationship(back_populates="owner")
