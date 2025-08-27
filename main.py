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

# --- CRUD ENDPOINTS ---

# SALES
@app.get("/sales", response_model=List[SaleSchema])
def read_sales(db: Session = Depends(get_db)):
    return db.query(Sale).all()

@app.post("/sales", response_model=SaleSchema, status_code=201)
def create_sale(sale: SaleCreateSchema, db: Session = Depends(get_db)):
    db_sale = Sale(**sale.dict())
    db.add(db_sale)
    db.commit()
    db.refresh(db_sale)
    return db_sale

@app.put("/sales/{sale_id}", response_model=SaleSchema)
def update_sale(sale_id: int, updated_sale: SaleCreateSchema, db: Session = Depends(get_db)):
    sale = db.query(Sale).filter(Sale.id == sale_id).first()
    if not sale:
        raise HTTPException(status_code=404, detail="Sale not found")
    for key, value in updated_sale.dict().items():
        setattr(sale, key, value)
    db.commit()
    db.refresh(sale)
    return sale

@app.delete("/sales/{sale_id}", status_code=204)
def delete_sale(sale_id: int, db: Session = Depends(get_db)):
    sale = db.query(Sale).filter(Sale.id == sale_id).first()
    if not sale:
        raise HTTPException(status_code=404, detail="Sale not found")
    db.delete(sale)
    db.commit()
    return

# CUSTOMERS
@app.get("/customers", response_model=List[CustomerSchema])
def read_customers(db: Session = Depends(get_db)):
    return db.query(Customer).all()

@app.post("/customers", response_model=CustomerSchema, status_code=201)
def create_customer(customer: CustomerCreateSchema, db: Session = Depends(get_db)):
    db_customer = Customer(**customer.dict())
    db.add(db_customer)
    db.commit()
    db.refresh(db_customer)
    return db_customer

@app.put("/customers/{customer_id}", response_model=CustomerSchema)
def update_customer(customer_id: int, updated_customer: CustomerCreateSchema, db: Session = Depends(get_db)):
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    for key, value in updated_customer.dict().items():
        setattr(customer, key, value)
    db.commit()
    db.refresh(customer)
    return customer

@app.delete("/customers/{customer_id}", status_code=204)
def delete_customer(customer_id: int, db: Session = Depends(get_db)):
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    db.delete(customer)
    db.commit()
    return

# PRODUCTS
@app.get("/products", response_model=List[ProductSchema])
def read_products(db: Session = Depends(get_db)):
    return db.query(Product).all()

@app.post("/products", response_model=ProductSchema, status_code=201)
def create_product(product: ProductCreateSchema, db: Session = Depends(get_db)):
    db_product = Product(**product.dict())
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product

@app.put("/products/{product_id}", response_model=ProductSchema)
def update_product(product_id: int, updated_product: ProductCreateSchema, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    for key, value in updated_product.dict().items():
        setattr(product, key, value)
    db.commit()
    db.refresh(product)
    return product

@app.delete("/products/{product_id}", status_code=204)
def delete_product(product_id: int, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    db.delete(product)
    db.commit()
    return

# EMPLOYEES
@app.get("/employees", response_model=List[EmployeeSchema])
def read_employees(db: Session = Depends(get_db)):
    return db.query(Employee).all()

@app.post("/employees", response_model=EmployeeSchema, status_code=201)
def create_employee(employee: EmployeeCreateSchema, db: Session = Depends(get_db)):
    db_employee = Employee(**employee.dict())
    db.add(db_employee)
    db.commit()
    db.refresh(db_employee)
    return db_employee

@app.put("/employees/{employee_id}", response_model=EmployeeSchema)
def update_employee(employee_id: int, updated_employee: EmployeeCreateSchema, db: Session = Depends(get_db)):
    employee = db.query(Employee).filter(Employee.id == employee_id).first()
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    for key, value in updated_employee.dict().items():
        setattr(employee, key, value)
    db.commit()
    db.refresh(employee)
    return employee

@app.delete("/employees/{employee_id}", status_code=204)
def delete_employee(employee_id: int, db: Session = Depends(get_db)):
    employee = db.query(Employee).filter(Employee.id == employee_id).first()
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    db.delete(employee)
    db.commit()
    return

# --- AI SQL ENDPOINT ---
@app.post("/ask")
def ask_sql(user_query: UserQuery, db: Session = Depends(get_db)):
    sql_query = generate_sql_query(user_query.query)

    # Bereinigen: Markdown-Tags entfernen
    sql_query_clean = re.sub(r"```(?:sql)?", "", sql_query, flags=re.IGNORECASE).strip()

    if not is_safe_sql_query(sql_query_clean):
        raise HTTPException(status_code=400, detail=f"Generated query is unsafe: {sql_query_clean}")

    try:
        result = db.execute(text(sql_query_clean))
        rows = [dict(row._mapping) for row in result]
        html_table = results_to_html_table(rows)
        return {"query": sql_query_clean, "results_html": html_table}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"SQL execution error: {str(e)}")
