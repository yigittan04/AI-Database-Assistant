# AI Database Assistant

An AI-powered database assistant built with **FastAPI**, **PostgreSQL**, **Redis**, and **Groq LLM**.

The application allows authenticated users to ask questions in natural language. The AI converts user requests into SQL queries, validates them for safety, executes them against a PostgreSQL database, and returns concise, human-readable responses.

---

# Live Application

**API**

https://ai-database-assistant-x12z.onrender.com

**Swagger Documentation**

https://ai-database-assistant-x12z.onrender.com/docs

---

# Architecture

```
                User
                  │
                  ▼
             FastAPI API
                  │
                  ▼
             Groq LLM
                  │
                  ▼
        SQL Safety Validation
                  │
                  ▼
        PostgreSQL (Neon)
                  ▲
                  │
        Redis (Sessions, Cache,
        Conversation History)
```

---

# Technologies Used

- FastAPI
- PostgreSQL (Neon)
- Redis (Upstash)
- Groq API (Llama 3.3 70B Versatile)
- Render
- Pydantic
- Argon2 Password Hashing (pwdlib)

---

# Features

- Natural language database queries
- AI-generated SQL queries
- SQL safety validation
- Secure user authentication
- Role-based access control
- Redis session management
- SQL query caching
- Prompt injection detection
- Automatic database migrations
- Error logging

---

# User Roles

## Administrator

Administrators can access information from:

- Users
- Employees
- Departments
- Messages

## Restricted User

Restricted users can access information from:

- Employees
- Departments

The AI receives a different database schema depending on the authenticated user's permissions.

---

# Security

The application includes several security mechanisms:

- Passwords are hashed using Argon2.
- Token-based authentication using Redis sessions.
- Prompt injection attempts are detected using keyword filtering.
- Only `SELECT` statements are allowed.
- SQL statements are validated before execution.
- Dangerous SQL operations are blocked.

Blocked SQL statements include:

- INSERT
- UPDATE
- DELETE
- DROP
- ALTER
- CREATE
- TRUNCATE

Additionally:

- Passwords are never returned from the database.
- Internal prompts and database schema are never exposed to users.
- Unexpected errors are logged internally instead of being shown to users.

---

# Redis Usage

Redis is used for:

- User session storage
- Conversation history (1 hour)
- SQL query caching (60 seconds)

---

# Error Handling

Unexpected errors are written to:

```
app.log
```

Users receive error messages instead of raw server or database errors.

---

# Database

**Database Provider**

Neon PostgreSQL

The database schema is created automatically using migration files.

No manual SQL execution is required after deployment.

---

# Deployment

**Hosting**

Render Web Service

---

# Environment Variables

The following environment variables are required:

```
DATABASE_URL
REDIS_URL
GROQ_API_KEY
```

Sensitive values are managed through Render Environment Variables and are not stored inside the source code.

---

# Database Migrations

Run database migrations:

```bash
python run_migrations.py
```

---

# Running Locally

Clone the repository:

```bash
git clone https://github.com/yigittan04/AI-Database-Assistant.git
```

Enter the project directory:

```bash
cd AI-Database-Assistant
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Create a `.env` file containing:

```
DATABASE_URL=...
REDIS_URL=...
GROQ_API_KEY=...
```

Run migrations:

```bash
python run_migrations.py
```

Start the application:

```bash
uvicorn main:app --reload
```

Swagger UI:

```
http://127.0.0.1:8000/docs
```

---

# Authentication

1. Send a request to:

```
POST /login
```

using a username and password.

2. Copy the returned authentication token.

3. Open Swagger (`/docs`).

4. Click **Authorize**.

5. Paste the token.

6. You can now access the protected endpoints.

---

# API Endpoints

| Method | Endpoint | Description |
|---------|----------|-------------|
| POST | `/login` | Authenticate user |
| POST | `/logout` | End current session |
| POST | `/chat` | Ask the AI database assistant |

---

# Project Structure

```
AI-Database-Assistant/
│
├── main.py
├── database.py
├── redis_client.py
├── security.py
├── run_migrations.py
├── migrations/
│   ├── 001_create_tables.sql
│   └── 002_seed_data.sql
├── static/
├── app.log
├── requirements.txt
├── .env
└── README.md
```