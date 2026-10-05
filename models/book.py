from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from models.user import User  # Avoid circular import issues

class Book(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str = Field(index=True)
    author: str = Field(index=True)
    price: int
    is_sold: bool = Field(default=False)

    # Foreign key to user table
    user_id: int = Field(foreign_key="user.id")
    owner: Optional["User"] = Relationship(back_populates="books")  # Assuming there's a User model with a back_populates relationship

# request body for creating a book
class BookCreate(SQLModel):
    title: str
    author: str
    price: int
    user_id: int

# response body 
class BookRead(SQLModel):
    id: int
    title: str
    author: str
    price: int
    is_sold: bool
    user_id: int

class BookUpdate(SQLModel):
    price: Optional[int] = None
    is_sold: Optional[bool] = None
        
