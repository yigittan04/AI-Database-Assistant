import psycopg2
import os
import json
from datetime import datetime, date
from decimal import Decimal
from dotenv import load_dotenv

load_dotenv()

def json_serial(obj):
    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    if isinstance(obj, Decimal):
        return float(obj)
    raise TypeError(f"Type {type(obj)} not serializable")

def get_connection():
    return psycopg2.connect(os.getenv("DB_URL"))

def run_query(sql: str):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(sql)
    rows = cur.fetchall()
    columns = [desc[0] for desc in cur.description]
    conn.close()
    
    
    raw = [dict(zip(columns, row)) for row in rows]
    return json.loads(json.dumps(raw, default=json_serial))

def save_message(user_id: int, role: str, message: str):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""INSERT INTO messages (user_id, role, message) VALUES (%s, %s, %s)""", (user_id, role, message))
    conn.commit()
    conn.close()