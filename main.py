from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from motor.motor_asyncio import AsyncIOMotorClient
from passlib.context import CryptContext
import jwt
from datetime import datetime, timedelta
from bson import ObjectId
from pydantic import BaseModel
from typing import Optional
from pymongo import DESCENDING, ASCENDING

# FastAPI instance
app = FastAPI()

# MongoDB Connection
MONGO_URI = "mongodb://localhost:27017"
DATABASE_NAME = "bookstore"
client = AsyncIOMotorClient(MONGO_URI)
db = client[DATABASE_NAME]

# JWT Config
SECRET_KEY = "supersecretkey"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Password Hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2 Scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

# Pydantic Models
class UserRegister(BaseModel):
    username: str
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

class Book(BaseModel):
    title: str
    author: str
    description: str
    publisher:str

# Helper Function: Create JWT Token
def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

# Helper Function: Hash Password
def get_password_hash(password):
    return pwd_context.hash(password)

# Helper Function: Verify Password
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

# Register Route (Now Accepting JSON Body)
@app.post("/register")
async def register(user: UserRegister):
    existing_user = await db.users.find_one({"username": user.username})
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already exists")

    hashed_password = get_password_hash(user.password)
    await db.users.insert_one({"username": user.username, "password": hashed_password})
    
    return {"message": "User registered successfully"}

# Login Route (Now Accepting JSON Body)
@app.post("/login")
async def login(user: UserLogin):
    db_user = await db.users.find_one({"username": user.username})
    
    if not db_user or not verify_password(user.password, db_user["password"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    access_token = create_access_token({"sub": db_user["username"]}, timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    return {"access_token": access_token, "token_type": "bearer"}

# Dependency: Get Current User from Token
async def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if not username:
            raise HTTPException(status_code=401, detail="Invalid token")
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    user = await db.users.find_one({"username": username})
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    
    return user

# Create Book
@app.post("/books")
async def create_book(book: Book, user: dict = Depends(get_current_user)):
    result = await db.books.insert_one(book.dict())
    return {"message": "Book added successfully", "book_id": str(result.inserted_id)}

# Bulk insert
@app.post("/books/bulkinsert")
async def bulk_insert(books: list[Book], user: dict = Depends(get_current_user)):
    documents = [item.dict() for item in books]
    result  = await db.books.insert_many(documents)
    return {"message": "Book's added successfully","result": [str(id) for id in result.inserted_ids]}
        

# get route with soritng and paging options.
@app.get("/books")
async def get_books(
    author: Optional[str] = None,
    publisher: Optional[str] = None,
    sort_by: Optional[str] = "title",  # Default sort by title
    sort_order: Optional[str] = "asc",  # Default to ascending order
    page: Optional[int] = 1,  # Default to the first page
    limit: Optional[int] = 10,  # Default to 10 items per page
    user: dict = Depends(get_current_user)
):
    query = dict()

    if author:
        query["author"] = author
    if publisher:
        query["publisher"] = publisher

    # Sorting logic based on query params
    if sort_order == "desc":
        sort_order = DESCENDING
    else:
        sort_order = ASCENDING

    # Create sort query (default sorting by title)
    sort_query = [(sort_by, sort_order)]

    # Pagination logic
    skip = (page - 1) * limit

    total_count = await db.books.count_documents(query)
    # Fetch books from the database
    books = []
    print("sort_query",sort_query)
    async for book in db.books.find(query).skip(skip).limit(limit).sort(sort_query):
        books.append({**book, "_id": str(book["_id"])})

    return {"rows":books,"count":total_count}

# get route with soritng and paging options.
@app.get("/books/local/sorting")
async def get_books(
    author: Optional[str] = None,
    publisher: Optional[str] = None,
    sort_by: Optional[str] = "title",  # Default sort by title
    sort_order: Optional[str] = "asc",  # Default to ascending order
    user: dict = Depends(get_current_user)
):
    query = dict()

    if author:
        query["author"] = author
    if publisher:
        query["publisher"] = publisher

    # Sorting logic based on query params
    reverse = False
    if sort_order == "desc":
        reverse = True

    # Fetch books from the database
    books = []

    async for book in db.books.find(query):
        books.append({**book, "_id": str(book["_id"])})
    books = sorted(books, key=lambda x: x[sort_by], reverse=reverse)
    return {"rows":books}

# Get Book by ID
@app.get("/books/{book_id}")
async def get_book(book_id: str, user: dict = Depends(get_current_user)):
    try:
        len(book_id)
        book = await db.books.find_one({"_id": ObjectId(book_id)})

        if not book:
            raise Exception()
            # raise HTTPException(status_code=404, detail="Book not found")
    
    except Exception:
        raise HTTPException(status_code=400, detail="Book not found.")
    return {**book, "_id": str(book["_id"])}

# Update Book
@app.put("/books/{book_id}")
async def update_book(book_id: str, book: Book, user: dict = Depends(get_current_user)):
    result = await db.books.update_one(
        {"_id": ObjectId(book_id)},
        {"$set": book.dict()}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Book not found")
    
    return {"message": "Book updated successfully"}

# Delete Book
@app.delete("/books/{book_id}")
async def delete_book(book_id: str, user: dict = Depends(get_current_user)):
    result = await db.books.delete_one({"_id": ObjectId(book_id)})
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Book not found")
    
    return {"message": "Book deleted successfully"}

# Run the Server
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
