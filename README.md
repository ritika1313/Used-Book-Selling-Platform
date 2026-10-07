# Used-Book-Selling-Platform
University Students needs a platform to buy and sell used textbook. Sellers list their books with a price &amp; buyers browse or search. When a book is purchased, the seller marks it as sold.
📚 Kitaab Exchange API — Interview Revision README
1. Project in One Line
Kitaab Exchange API is a REST API for a used-book exchange/selling platform where users can register, list books, search available books, and mark books as sold.
2. Tech Stack
- Python — programming language
- FastAPI — backend/API framework
- SQLModel — ORM + data validation
- SQLite — relational database
- Uvicorn — ASGI server
- Postman / Swagger UI — API testing
3. Main Features
1. User registration
2. Add/list a used book
3. Search books by title or author
4. Show only available/unsold books
5. Mark a book as sold
6. API-key authentication for protected operations
7. User–book one-to-many relationship
8. Request/response validation using SQLModel models
4. Project Structure
project/
├── main.py
├── database.py
├── auth.py
├── routes/
│   ├── books.py
│   └── users.py
└── models/
    ├── book.py
    └── user.py
What each file does
File	Responsibility
main.py	Creates FastAPI app and includes routers
database.py	Creates DB engine and provides DB sessions
auth.py	API-key authentication
routes/books.py	Book-related endpoints
routes/users.py	User-related endpoints
models/book.py	Book table + request/response schemas
models/user.py	User table + request/response schemas


5. Architecture
Client / Postman / Frontend
            ↓
         FastAPI
            ↓
     ┌──────┴──────┐
     ↓             ↓
 Users Router   Books Router
     ↓             ↓
        SQLModel ORM
              ↓
           SQLite
              ↓
       User Table / Book Table
Protected request flow
Request
   ↓
Depends(verify_api_key)
   ↓
Read X-API-Key header
   ↓
Validate API key
   ↓
Valid → Endpoint executes
Invalid → 401 error
6. Important API Endpoints
Users
Register User
POST /users/
Protected by API key.
Example body:
{
  "name": "Riya",
  "email": "riya@gmail.com",
  "college": "ABC College"
}
List Users
GET /users/
Currently public in this project.
Books
List/Search Available Books
GET /books/
Optional query parameters:
/books/?title=java
/books/?author=robert
Only books where:
Book.is_sold == False
are returned.
Create Book
POST /books/
Protected.
Example:
{
  "title": "Clean Code",
  "author": "Robert Martin",
  "price": 500,
  "user_id": 1
}
Update Book
PATCH /books/{book_id}/sell
Protected.
Can update fields provided in BookUpdate, such as:
{
  "price": 400
}
or:
{
  "is_sold": true
}
Mark Book as Sold
PATCH /books/{book_id}/sold
Protected.
It changes:
book.is_sold = True
After that, the book no longer appears in the available-book listing.
7. Database Design
User Table
User
----------------
id          PK
name
email       UNIQUE
college
Book Table
Book
----------------
id          PK
title       INDEX
author      INDEX
price
is_sold
user_id     FK → User.id
Relationship
One user can have many books.
User 1 ─────────── N Books
This is a one-to-many relationship.
8. SQLModel Concepts
table=True
class Book(SQLModel, table=True):
It tells SQLModel that the class represents a database table.
Primary Key
id: Optional[int] = Field(default=None, primary_key=True)
A primary key uniquely identifies each row.
Foreign Key
user_id: int = Field(foreign_key="user.id")
It connects a book to its owner.
Index
title: str = Field(index=True)
author: str = Field(index=True)
Indexes improve lookup/search performance.
Unique
email: str = Field(unique=True)
Two users cannot have the same email.
9. Why Separate Models?
The project uses different models for different purposes.
Database Model
Book
Represents the actual database table.
Create Model
BookCreate
Defines what the client must send when creating a book.
Read Model
BookRead
Defines what the API returns.
Update Model
BookUpdate
Defines fields that can be changed.
Interview Answer
"I separated database models from request and response schemas so that the API does not directly expose the database structure and each operation has the appropriate fields."

10. FastAPI Dependency Injection
The project uses:
Depends()
Example:
session: Session = Depends(get_session)
FastAPI automatically calls get_session() and provides the database session to the endpoint.
Authentication:
api_key: str = Depends(verify_api_key)
FastAPI automatically runs the authentication dependency before the endpoint.
Interview Answer
"Depends() allows FastAPI to inject reusable dependencies such as database sessions and authentication logic into endpoints."

11. Database Session Flow
def get_session():
    with Session(engine) as session:
        yield session
Endpoint:
session: Session = Depends(get_session)
Then:
session.add(book)
session.commit()
session.refresh(book)
Meaning
- add() → adds object to the session
- commit() → saves changes to database
- refresh() → gets the latest database state
Interview Answer
"I use FastAPI dependency injection to create and manage a database session for each request."

12. Authentication
The project uses API-key based authentication.
In auth.py:
def verify_api_key(x_api_key: str = Header(...)):
    if x_api_key != API_KEY:
        raise HTTPException(
            status_code=401,
            detail="Invalid API Key"
        )
The client sends:
X-API-Key: secret123
Protected endpoint example
api_key: str = Depends(verify_api_key)
Interview Answer
"I implemented API-key authentication using FastAPI dependency injection. A reusable verify_api_key dependency validates the X-API-Key header before protected endpoints execute."

13. Authentication vs Authorization
Authentication
Who are you?
Example:
Is the API key valid?
Authorization
What are you allowed to do?
Example:
Can this user update this particular book?
Important Project Limitation
The current API-key system only authenticates the request.
It does not identify individual users or verify book ownership.
Production Improvement
"For production, I would use user-based authentication such as JWT and add authorization checks so only the book owner can update or sell their book."

14. Public vs Protected APIs
Public
GET /books/
GET /users/
Protected
POST /books/
PATCH /books/{id}/sell
PATCH /books/{id}/sold
POST /users/
General rule:
Read operations can be public, while operations that modify data are protected.

15. Searching Books
The endpoint accepts optional query parameters:
title: Optional[str] = Query(default=None)
author: Optional[str] = Query(default=None)
Then:
if title:
    query = query.where(Book.title.contains(title))
This allows requests like:
GET /books/?title=java
Path vs Query Parameter
Path parameter:
/books/5
Used to identify a specific resource.
Query parameter:
/books/?title=java
Used for filtering/searching.
Interview Answer
"I use path parameters when identifying a specific book and query parameters for optional filtering such as title and author."

16. Why is_sold?
Instead of deleting a sold book, the project keeps the record and changes:
is_sold = True
This is useful because the transaction/history remains in the database.
Available books are filtered using:
Book.is_sold == False
Interview Answer
"I used a boolean is_sold flag so sold books remain stored while being excluded from the available-book listing."

17. PATCH and Partial Update
The project uses:
PATCH
for updates.
Example:
{
  "price": 400
}
Only the provided field should change.
This is why the code uses:
updates.model_dump(exclude_unset=True)
It returns only the fields supplied by the client.
Then:
setattr(book, key, value)
updates those fields dynamically.
Interview Answer
"I used PATCH for partial updates. exclude_unset=True ensures that fields not provided by the client are not overwritten."

18. Error Handling
Book not found
raise HTTPException(
    status_code=404,
    detail="Book not found"
)
Invalid API key
raise HTTPException(
    status_code=401,
    detail="Invalid API Key"
)
Duplicate email
raise HTTPException(
    status_code=400,
    detail="Email already registered"
)
Important
With the current code, a missing required X-API-Key header is rejected by FastAPI validation before verify_api_key() receives a value. In practice, this is typically a 422 response, while a supplied-but-wrong API key produces 401.
19. Important Code Flow: Creating a Book
POST /books/
      ↓
Request body → BookCreate
      ↓
verify_api_key()
      ↓
get_session()
      ↓
Book.model_validate(book_date)
      ↓
session.add(book)
      ↓
session.commit()
      ↓
session.refresh(book)
      ↓
BookRead response
Interview Answer
"The request is first validated using BookCreate, authentication is handled through a dependency, the book is converted into the database model, saved using the SQLModel session, and returned using BookRead."

20. Important Code Flow: Selling a Book
PATCH /books/{id}/sold
          ↓
verify API key
          ↓
Find book by ID
          ↓
Book exists?
      ↙         ↘
    No           Yes
    ↓             ↓
   404       is_sold = True
                  ↓
               commit
                  ↓
              return book
21. Why FastAPI?
Interview Answer
"I chose FastAPI because it is lightweight, supports automatic request validation, dependency injection, automatic Swagger documentation, and works well for building REST APIs."

22. Why SQLModel?
Interview Answer
"I used SQLModel because it combines Pydantic-style data validation with SQLAlchemy-based ORM functionality, so I can define models and interact with the database using Python classes."

23. Why SQLite?
Interview Answer
"I used SQLite because it is lightweight, requires no separate database server, and is sufficient for a small academic project. For production, I would prefer PostgreSQL."

24. Why APIRouter?
router = APIRouter(
    prefix="/books",
    tags=["books"]
)
It keeps the application modular.
Instead of putting every endpoint inside main.py, users and books have separate route files.
Interview Answer
"I used APIRouter to organize endpoints by feature, which keeps the code modular and maintainable."

25. response_model
Example:
@router.get(
    "/",
    response_model=list[BookRead]
)
It defines the expected response structure.
Benefits:
- Response validation
- Consistent API output
- Automatic Swagger documentation
- Prevents unwanted fields from being exposed
26. Most Important Interview Questions
Q1. Explain your project.
"My project is a used-book exchange platform for college students. I developed the backend using FastAPI and SQLModel with SQLite. Users can register, sellers can list books, and buyers can search available books by title or author. When a book is sold, its is_sold field becomes true, so it is removed from the available-book listing. I also implemented API-key authentication for protected operations and a one-to-many relationship between users and books."

Q2. How did you implement authentication?
"I used API-key based authentication with FastAPI dependency injection. I created a reusable verify_api_key function that validates the X-API-Key header. Protected routes use Depends(verify_api_key)."

Q3. Why did you use Depends()?
"Depends() allows FastAPI to execute reusable logic automatically before the endpoint. I used it for authentication and database session management."

Q4. What happens when the API key is invalid?
"The dependency raises an HTTP 401 error and the endpoint business logic is not executed."

Q5. What happens when the API key is missing?
"Because the header is required using Header(...), FastAPI validation rejects the request before the endpoint executes, typically with a 422 response."

Q6. What is the relationship between User and Book?
"It is a one-to-many relationship. One user can own multiple books, while each book belongs to one user through the user_id foreign key."

Q7. Why use a foreign key?
"The foreign key maintains the relationship between the book and its owner and helps maintain referential integrity."

Q8. Why use BookCreate, BookRead, and BookUpdate separately?
"They represent different API responsibilities. BookCreate validates input for creation, BookRead controls the response, and BookUpdate contains only fields that can be updated."

Q9. Why use exclude_unset=True?
"It ensures that during a PATCH request only the fields actually provided by the client are updated."

Q10. Why use is_sold instead of deleting the book?
"It preserves the book record while allowing the application to hide sold books from the available listing."

Q11. What is the difference between 401 and 404?
"401 means authentication failed or is missing. 404 means the requested resource was not found."

Q12. What is the difference between authentication and authorization?
"Authentication verifies who the user is. Authorization verifies what that user is allowed to do."

Q13. Is your authentication production-ready?
"The current API-key approach is suitable for this academic project, but for production I would store secrets in environment variables or a secret manager and use user-based authentication such as JWT with authorization checks."

Q14. Why not use PostgreSQL?
"SQLite was sufficient for this small academic project because it is simple and requires no separate database server. For a production multi-user system, I would use PostgreSQL."

Q15. How would you improve this project?
Good answer:
"I would add JWT-based user authentication, role or ownership-based authorization, password hashing, PostgreSQL, database migrations, better validation, pagination, and proper environment-based configuration."

27. Potential Weak Points Interviewer May Notice
1. Hardcoded API key
Current:
API_KEY = "secret123"
Say:
"For production, I would move this to an environment variable or secret manager."

2. No password authentication
Current project uses API key.
Say:
"The project uses a simple API-key mechanism for demonstration. A production application should use proper user authentication."

3. No ownership check
Currently, knowing the book ID and valid API key is enough to attempt an update.
Improvement:
authenticated user
        ↓
book.user_id == current_user.id
        ↓
allow update
4. Duplicate update endpoints
There are two endpoints:
PATCH /books/{id}/sell
PATCH /books/{id}/sold
The /sold endpoint is specifically for marking a book sold.
If asked:
"There is some overlap in the current design. I would simplify the API by keeping a single clear update endpoint or keeping /sold as a dedicated business action."

5. No pagination
Currently:
session.exec(query).all()
could return many records.
Production improvement:
?page=1&limit=20
28. Production Architecture You Can Mention
Frontend
   ↓
FastAPI
   ↓
JWT Authentication
   ↓
Authorization / Ownership Check
   ↓
Service Layer
   ↓
SQLModel / SQLAlchemy
   ↓
PostgreSQL
Additional production components:
Environment Variables
Password Hashing
Database Migrations
Pagination
Logging
Testing
Docker
CI/CD
29. 30-Second Revision
Remember these 10 points:
1. FastAPI → REST API framework
2. SQLModel → ORM + validation
3. SQLite → database
4. APIRouter → modular routes
5. Depends() → dependency injection
6. API key → current authentication
7. User → Books → one-to-many
8. user_id → foreign key
9. is_sold → availability status
10. BookCreate/Read/Update → API schemas
30. 60-Second Project Answer
"My project is a used-book exchange platform designed mainly for college students. I built the backend using FastAPI, SQLModel, and SQLite. The application has separate routers for users and books. Users can register, sellers can add books with title, author and price, and buyers can search available books using title or author. I used an is_sold flag so that when a book is sold, it remains in the database but is excluded from the available-book listing. I also implemented API-key authentication using FastAPI's dependency injection, so protected operations such as creating or updating books require a valid API key. SQLModel handles the database models and relationships, with a one-to-many relationship between users and books. I also separated request and response schemas using BookCreate, BookRead, and BookUpdate to keep the API structured and maintainable."

31. Final Interview Formula
When interviewer asks "Why did you use X?", answer:
What it is
      +
Why you used it
      +
Benefit in your project
Example:
"I used FastAPI as the backend framework because it provides automatic validation, dependency injection, and API documentation, which made it suitable for building this REST API."
