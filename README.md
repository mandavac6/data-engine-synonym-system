# Data Engine Synonym System


## 📌 Overview

The **Data Engine Synonym System** is a FastAPI-based application that retrieves synonym data from a SQL Server database and supports caching for better performance. It includes both in-memory and Redis-based caching strategies.

---

## ✅ Functional Requirements

### 🔍 Synonym Retrieval

- Fetches all synonym records from a SQL Server database
- Each record includes:
  - Unique word ID
  - Word
  - List of synonyms
- Only **bulk retrieval** is supported (no single word lookup)
- Results show if they came from the **cache** or the **database**

### ⚙️ Caching

- Supports:
  - In-memory caching
  - Redis-based distributed caching
- Cache features:
  - Configurable **Time-To-Live (TTL)**
  - Automatic **expiration**

---

## 🚀 Performance Requirements

- Uses cache to reduce database load
- Cache access is faster than database queries
- Database connections use pooling
- Cache operations are atomic and thread-safe

---

## 🛠 Architecture Notes

- App is built with **FastAPI**
- Use **SQLModel** and **SQLAlchemy** for database operations

---

## 📚 Tech Stack

- FastAPI
- SQLLite
- SQLModel
- SQLAlchemy
- Redis
- In-memory cache (like `functools.lru_cache`)
- Docker
- Swagger

---

## 🧪 How to Use This App

### 🔧 Setup Instructions

### Clone the repository:

       git clone https://github.com/your-username/data-engine-synonym-system.git
       cd data-engine-synonym-system

### Create and activate a virtual environment:

        python -m venv venv
        venv\Scripts\activate    # For Windows
        source venv/bin/activate # For Mac/Linux
    
### Install dependencies:

        pip install -r requirements.txt

### Run the FastAPI server:

        fastapi dev main.py

### Open the Swagger API Docs:
    
    Open your browser and go to:
        👉 http://127.0.0.1:8000/docs
