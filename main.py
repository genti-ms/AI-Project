# Update-Test: 27.08.2025
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List
from pydantic import BaseModel
from datetime import date
from dotenv import load_dotenv
import os
import openai
import re

from database import SessionLocal, engine
from models import Base, Sale, Customer, Product, Employee

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
    allow_origins=["*"],  # dev
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

# --- SQL GENERATION ---
def generate_sql_query(user_message: str) -> str:
    schema_hint = """
    Table: sales
      - id (int)
      - customer_id (int)
      - product_id (int)
      - employee_id (int)
      - quantity (int)
      - total_amount (float)
      - sale_date (date)
      - city (string)

    Table: customers
      - id (int)
      - name (string)
      - email (string)
      - city (string)
      - country (string)

    Table: products
      - id (int)
      - name (string)
      - description (string)
      - price (float)
      - stock (int)

    Table: employees
      - id (int)
      - first_name (string)
      - last_name (string)
      - email (string)
      - position (string)
    """

    prompt = [
        {"role": "system",
         "content": f"""
You are an SQL expert. Convert user input into SQL SELECT statements only.
Do NOT generate DELETE, UPDATE, INSERT, DROP, ALTER, TRUNCATE.
Use LIMIT if user requests "first" or "top".
Respond only with SQL, no explanation.

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
    return query

def is_safe_sql_query(query: str) -> bool:
    cleaned = query.strip().lower()
    if not cleaned.startswith("select"):
        return False
    unsafe_keywords = ["delete", "drop", "update", "insert", "alter", "truncate"]
    for keyword in unsafe_keywords:
        if re.search(rf"\b{keyword}\b", cleaned):
            return False
    return True

def results_to_html_table(results):
    if not results:
        return "<p>No results found.</p>"

    columns = results[0].keys()
    html = '<table border="1" cellpadding="5" cellspacing="0" style="border-collapse: collapse;">'
    html += "<thead><tr>"
    for col in columns:
        html += f"<th>{col}</th>"
    html += "</tr></thead>"

    html += "<tbody>"
    for row in results:
        html += "<tr>"
        for col in columns:
            html += f"<td>{row[col]}</td>"
        html += "</tr>"
    html += "</tbody></table>"

    return html

# --- SCHEMAS ---
class SaleSchema(BaseModel):
    id: int
    customer_id: int
    product_id: int
    employee_id: int
    quantity: int
    total_amount: float
    sale_date: date
    city: str

    class Config:
        orm_mode = True

class SaleCreateSchema(BaseModel):
    customer_id: int
    product_id: int
    employee_id: int
    quantity: int
    total_amount: float
    sale_date: date
    city: str

    class Config:
        orm_mode = True

class CustomerSchema(BaseModel):
    id: int
    name: str
    email: str
    city: str
    country: str

    class Config:
        orm_mode = True

class CustomerCreateSchema(BaseModel):
    name: str
    email: str
    city: str
    country: str

    class Config:
        orm_mode = True

class ProductSchema(BaseModel):
    id: int
    name: str
    description: str
    price: float
    stock: int

    class Config:
        orm_mode = True

class ProductCreateSchema(BaseModel):
    name: str
    description: str
    price: float
    stock: int

    class Config:
        orm_mode = True

class EmployeeSchema(BaseModel):
    id: int
    first_name: str
    last_name: str
    email: str
    position: str

    class Config:
        orm_mode = True

class EmployeeCreateSchema(BaseModel):
    first_name: str
    last_name: str
    email: str
    position: str

    class Config:
        orm_mode = True

class UserQuery(BaseModel):
    query: str

# --- AI SQL ENDPOINT ---
@app.post("/ask")
def ask_sql(user_query: UserQuery, db: Session = Depends(get_db)):
    sql_query = generate_sql_query(user_query.query)

    # Bereinigen: Markdown-Tags entfernen
    sql_query_clean = re.sub(r"```(?:sql)?", "", sql_query, flags=re.IGNORECASE).strip()

    if not is_safe_sql_query(sql_query_clean):
        raise HTTPException(status_code=400, detail=f"Generated query is unsafe: {sql_query_clean}")

    # Nonsense-Abfanglogik mit Zeilenumbruch
    generic_queries = [
        "select * from sales",
        "select * from customers",
        "select * from products",
        "select * from employees"
    ]
    if sql_query_clean.lower() in generic_queries:
        raise HTTPException(
            status_code=400,
            detail="⚠️ Hinweis:\n❌ Ich konnte deine Eingabe nicht verstehen.\n       Formuliere deine Eingabe klarer, was du wissen möchtest\n👉 Bitte probiere es nochmal."
        )

    try:
        result = db.execute(text(sql_query_clean))
        rows = [dict(row._mapping) for row in result]
        html_table = results_to_html_table(rows)
        return {"query": sql_query_clean, "results_html": html_table}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"SQL execution error: {str(e)}")
