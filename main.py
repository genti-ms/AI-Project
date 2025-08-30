# Letzte bearbeitung 30.08
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text
from pydantic import BaseModel
from dotenv import load_dotenv
import os
import openai
import re

from database import SessionLocal, engine
from models import Base

from fastapi.middleware.cors import CORSMiddleware

# --- ENVIRONMENT ---
load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")
if not openai_api_key:
    raise ValueError("OpenAI API key not found")
openai.api_key = openai_api_key

# --- APP ---
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- DATABASE ---
def init_db():
    Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.on_event("startup")
def on_startup():
    init_db()

# --- Pydantic Schema ---
class UserQuery(BaseModel):
    query: str

# --- Helper Functions ---
def is_safe_sql_query(query: str) -> bool:
    cleaned = query.strip().lower()
    if not cleaned.startswith("select"):
        return False
    unsafe_keywords = ["delete", "drop", "update", "insert", "alter", "truncate"]
    return all(keyword not in cleaned for keyword in unsafe_keywords)

def results_to_html_table(results):
    if not results:
        return "<p>No results found.</p>"
    columns = results[0].keys()
    html = '<table border="1" cellpadding="5" cellspacing="0" style="border-collapse: collapse;">'
    html += "<thead><tr>" + "".join(f"<th>{col}</th>" for col in columns) + "</tr></thead><tbody>"
    for row in results:
        html += "<tr>" + "".join(f"<td>{row.get(col, '—')}</td>" for col in columns) + "</tr>"
    html += "</tbody></table>"
    return html

# --- SQL Post-Processing ---
def fix_sql_for_sqlite(query: str) -> str:
    # SQLite-kompatible Datumsfunktionen
    query = re.sub(r"CURDATE\(\)", "date('now')", query, flags=re.IGNORECASE)
    query = re.sub(r"NOW\(\)\s*-\s*INTERVAL\s+(\d+)\s+DAY", r"date('now','-\1 days')", query, flags=re.IGNORECASE)
    # Leerzeichen nach AS, FROM, GROUP BY, ORDER BY
    query = re.sub(r"AS(\w)", r"AS \1", query)
    query = re.sub(r"FROM(\w)", r"FROM \1", query)
    query = re.sub(r"GROUPBY", "GROUP BY", query, flags=re.IGNORECASE)
    query = re.sub(r"ORDERBY", "ORDER BY", query, flags=re.IGNORECASE)
    query = re.sub(r"DESC(LIMIT)", r"DESC \1", query, flags=re.IGNORECASE)
    query = re.sub(r"WHERE(\w)", r"WHERE \1", query)
    return query.strip()

def generate_sql_query(user_message: str) -> str:
    schema_hint = """
    Table: sales
      - id, customer_id, product_id, employee_id, quantity, total_amount, sale_date, city
    Table: customers
      - id, name, email, city, country, created_at
    Table: products
      - id, name, category, price, stock, created_at
    Table: employees
      - id, name, region, hire_date
    """
    prompt = [
        {"role": "system", "content": f"""
You are an SQL expert. Convert user input into SQL SELECT statements only.
Rules:
- Use only SELECT (no DELETE, UPDATE, etc.)
- 'neueste/r', 'letzte/r', 'aktuelle/r' → ORDER BY <date_field> DESC LIMIT 1
- 'älteste/r' → ORDER BY <date_field> ASC LIMIT 1
- 'letzten X' → ORDER BY <date_field> DESC LIMIT X
- 'wie viele' → SELECT COUNT(*) AS count ...
- 'am meisten gekauft/verkauft/beliebt':
   * customers → GROUP BY customer_id ORDER BY SUM(total_amount) DESC
   * products → GROUP BY product_id ORDER BY SUM(quantity) DESC LIMIT 1
- 'Top X' → ORDER BY SUM(...) DESC LIMIT X
Use SQLite date syntax: date('now'), date('now','-X days')
Database schema:
{schema_hint}
""" },
        {"role": "user", "content": user_message}
    ]

    response = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=prompt,
        temperature=0,
        max_tokens=150
    )

    query = response.choices[0].message.content.strip()
    query = re.sub(r"[\n;]+", "", query)
    if "first" in user_message.lower() and "limit" not in query.lower():
        query += " LIMIT 1"
    return fix_sql_for_sqlite(query)

# --- Endpoint ---
@app.post("/ask")
def ask_sql(user_query: UserQuery, db: Session = Depends(get_db)):
    sql_query = generate_sql_query(user_query.query)
    sql_query_clean = re.sub(r"```(?:sql)?", "", sql_query, flags=re.IGNORECASE).strip()

    if not is_safe_sql_query(sql_query_clean):
        raise HTTPException(status_code=400, detail=f"Generated query is unsafe: {sql_query_clean}")

    # Verhindert generische SELECT * ohne klare Absicht
    user_query_lower = user_query.query.lower()
    is_all = any(keyword in user_query_lower for keyword in ["alle", "all"])
    generic_queries = ["select * from sales", "select * from customers", "select * from products", "select * from employees"]
    if sql_query_clean.lower() in generic_queries and not is_all:
        raise HTTPException(
            status_code=400,
            detail="⚠️ Hinweis:\n❌ Ich konnte deine Eingabe nicht verstehen.\nFormuliere deine Eingabe klarer."
        )

    try:
        result = db.execute(text(sql_query_clean))
        rows = [dict(row._mapping) for row in result]
        html_table = results_to_html_table(rows)
        return {"query": sql_query_clean, "results_html": html_table}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"SQL execution error: {str(e)}")
