# FastAPI Bookstore API

This project is a **FastAPI-based Bookstore API** with **JWT authentication**, **MongoDB** as the database, and support for **CRUD operations** on books. It accepts both **request body (JSON)** and **query parameters** in API requests.

---

## 🚀 Features
- User **Registration & Login** with hashed passwords.
- **JWT Authentication** for secure API access.
- **MongoDB Integration** using `motor`.
- **CRUD Operations** on books.
- **Supports both request body and query parameters**.

---

### 2️⃣ **Create Virtual Environment** (Optional but Recommended)
```bash
python -m venv venv
source venv/bin/activate  # macOS/Linux
venv\Scripts\activate    # Windows
```

### 3️⃣ **Install Dependencies**
```bash
pip install -r requirments.txt
```

### 4️⃣ **Run MongoDB Locally**
Ensure MongoDB is running on your system or use a remote MongoDB instance.

For local MongoDB:
```bash
mongod --dbpath /data/db  # Change path as per your system
```

---

## 🔑 API Authentication
This API uses **JWT (JSON Web Token)** for authentication. Obtain a token by logging in and include it in the `Authorization` header for protected routes.

---

## 📌 API Endpoints

### **1️⃣ Register User**
**Endpoint:** `POST /register`
```json
{
  "username": "testuser",
  "password": "securepassword"
}
```
_Response:_
```json
{
  "message": "User registered successfully"
}
```

---

### **2️⃣ Login User (Get JWT Token)**
**Endpoint:** `POST /login`
```json
{
  "username": "testuser",
  "password": "securepassword"
}
```
_Response:_
```json
{
  "access_token": "your.jwt.token",
  "token_type": "bearer"
}
```

---

### **3️⃣ Create a Book**
**Endpoint:** `POST /books`
**Headers:**
```
Authorization: Bearer your.jwt.token
```
**Body (JSON):**
```json
{
  "title": "The Alchemist",
  "author": "Paulo Coelho",
  "description": "A book about following your dreams."
}
```
_Response:_
```json
{
  "message": "Book added successfully",
  "book_id": "65a1234567890abcdef"
}
```

---

### **4️⃣ Get All Books**
**Endpoint:** `GET /books`
**Headers:**
```
Authorization: Bearer your.jwt.token
```
_Response:_
```json
[
  {
    "_id": "65a1234567890abcdef",
    "title": "The Alchemist",
    "author": "Paulo Coelho",
    "description": "A book about following your dreams."
  }
]
```

---

### **5️⃣ Get a Book by ID**
**Endpoint:** `GET /books/{book_id}`
**Example:** `/books/65a1234567890abcdef`

---

### **6️⃣ Update a Book**
**Endpoint:** `PUT /books/{book_id}`
```json
{
  "title": "The Alchemist (Updated)",
  "author": "Paulo Coelho",
  "description": "Updated description."
}
```

---

### **7️⃣ Delete a Book**
**Endpoint:** `DELETE /books/{book_id}`
**Example:** `/books/65a1234567890abcdef`

---

## 🏃 Running the Server
Run the FastAPI server with **Uvicorn**:
```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

The API will be available at: **`http://127.0.0.1:8000`**

### 🔍 **Interactive API Docs:**
FastAPI provides automatic API documentation:
- Swagger UI: **[http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)**
- ReDoc UI: **[http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)**

---

## 🛠️ Troubleshooting
- **Error `Could not import module "main"`?**
  - Ensure you run `uvicorn` from the same directory where `main.py` is located.
  - Try running: `python -m uvicorn main:app --reload`

- **MongoDB not connecting?**
  - Ensure MongoDB service is running (`mongod` process is active).
  - Use a **valid MongoDB connection string** (`mongodb://localhost:27017`).

---

## 💡 Contributing
Feel free to fork and improve this API! Submit pull requests if you add new features.

---

## 📜 License
This project is licensed under the MIT License.

---

## 💬 Need Help?
For any questions, open an issue or contact the author.

Happy Coding! 🚀

