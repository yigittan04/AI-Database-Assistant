from fastapi import FastAPI, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from groq import Groq
from database import run_query, run_write, get_connection
from redis_client import (
    get_history, save_history,
    get_cached_query, cache_query, invalidate_cache,
    create_session, get_session, delete_session
)
import os, re
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])
app.mount("/static", StaticFiles(directory="static"), name="static")

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

DB_SCHEMA = """
Tables:
- users(id, name, is_admin, created_at)
- messages(id, user_id, message, created_at)

Relationships:
- messages.user_id -> users.id
"""

def build_system_prompt(is_admin: bool) -> str:
    return f"""You are a database assistant for a PostgreSQL database.

{DB_SCHEMA}

Authorization: {"ADMIN can read and write to the database." if is_admin else "Read-only users can only retrieve data, never modify it."}

Rules:
- To read data, wrap your SQL in <sql_query>...</sql_query> tags.
- To write data (INSERT/UPDATE/DELETE), wrap in <sql_write>...</sql_write> tags.
- Only use <sql_write> if the user is ADMIN.
- Never use DROP, TRUNCATE, or ALTER under any circumstances.
- Always explain results in plain, helpful language.

SQL Rules — follow these strictly:
- Never SELECT a non-aggregated column alongside COUNT(*) or other aggregates without including it in GROUP BY.
- To count all users: SELECT COUNT(*) as total FROM users;
- To see when users were added: SELECT id, name, created_at FROM users ORDER BY created_at;
- To count AND see details together: SELECT DATE(created_at) as day, COUNT(*) as signups FROM users GROUP BY DATE(created_at) ORDER BY day;
- Always use column aliases (AS) to make results readable.
- When in doubt, use multiple separate queries rather than one complex one.
- Never select password column.
"""


class LoginRequest(BaseModel):
    name: str
    password: str

@app.post("/login")
def login(req: LoginRequest):
    connect = get_connection()
    cursor = connect.cursor()
    cursor.execute(
        "SELECT id, name, password, is_admin FROM users WHERE name = %s",
        (req.name,)
    )
    row = cursor.fetchone()
    connect.close()

    if not row:
        raise HTTPException(status_code=401, detail="Invalid name or password")

    user_id, name, stored_password, is_admin = row

    if req.password != stored_password:
        raise HTTPException(status_code=401, detail="Invalid name or password")

    token = create_session(str(user_id), is_admin)
    return {"token": token, "is_admin": is_admin}





@app.post("/logout")
def logout(authorization: str = Header(...)):
    token = authorization.replace("Bearer ", "")
    delete_session(token)
    return {"status": "logged out"}





class ChatRequest(BaseModel):
    message: str
    session_id: str

@app.post("/chat")
def chat(req: ChatRequest, authorization: str = Header(...)):


    token = authorization.replace("Bearer ", "")
    session = get_session(token)
    if not session:
        raise HTTPException(status_code=401, detail="Invalid session")

    is_admin = session["is_admin"]
    system = build_system_prompt(is_admin)



    history = get_history(req.session_id)
    messages = history + [{"role": "user", "content": req.message}]

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "system", "content": system}] + messages,
        max_tokens=1000,
        temperature=0.3
    )
    reply = response.choices[0].message.content




    sql_query_match = re.search(r"<sql_query>(.*?)</sql_query>", reply, re.DOTALL)
    if sql_query_match:
        sql = sql_query_match.group(1).strip()
        try:
            results = get_cached_query(sql)
            if results is None:
                results = run_query(sql)
                if results is None:
                    results = run_query(sql)
                    results = [{k: v for k, v in row.items() if k != "password"} for row in results]
                cache_query(sql, results, ttl=60)
                
            followup = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[{"role": "system", "content": system}] + messages + [
                    {"role": "assistant", "content": reply},
                    {"role": "user", "content": f"Query result: {results}\n\nSummarize for the user in plain language."}
                ],
                max_tokens=1000,
                temperature=0.3
            )
            final_reply = followup.choices[0].message.content
        except Exception as e:
            final_reply = f"Database error: {str(e)}"




    elif sql_write_match := re.search(r"<sql_write>(.*?)</sql_write>", reply, re.DOTALL):
        if not is_admin:
            final_reply = "You can't modify the database."
        else:
            try:
                sql = sql_write_match.group(1).strip()
                result = run_write(sql)
                invalidate_cache()
                final_reply = f"Database updated. ({result['rows_affected']} row(s) affected)"
            except Exception as e:
                final_reply = f"Write error: {str(e)}"
    else:
        final_reply = reply



    history.append({"role": "user", "content": req.message})
    history.append({"role": "assistant", "content": final_reply})
    save_history(req.session_id, history)

    return {"reply": final_reply}