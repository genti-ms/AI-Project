from fastapi import FastAPI, Depends, Body, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text  # <-- hier importieren
from typing import List
from pydantic import BaseModel
from datetime import date
from dotenv import load_dotenv
import os
import openai
import json
import re

from schemas import GeneratedTextCreate, GeneratedTextResponse
from database import SessionLocal, engine
from models import Base, Sale, Customer, Product, Employee, GeneratedText
from fastapi.middleware.cors import CORSMiddleware

# Umgebungsvariablen laden
load_dotenv()

# OpenAI API-Key aus Umgebungsvariablen lesen
openai_api_key = os.getenv("OPENAI_API_KEY")
if not openai_api_key:
    raise ValueError("OpenAI API key not found in environment variables")

openai.api_key = openai_api_key

database_url = os.getenv("DATABASE_URL")

# FastAPI-App initialisieren
app = FastAPI()

# CORS Middleware konfigurieren (Cross-Origin Resource Sharing)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Erlaube alle Ursprünge (für Entwicklung; ggf. einschränken in Produktion)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def init_db():
    """
    Datenbank-Tabellen erstellen, falls noch nicht vorhanden.
    Wird beim Startup ausgeführt.
    """
    Base.metadata.create_all(bind=engine)


def get_db():
    """
    Liefert eine Datenbank-Session (Dependency für FastAPI).
    Stellt sicher, dass die Session nach Verwendung geschlossen wird.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.on_event("startup")
def on_startup():
    """
    Event-Handler beim Start der App.
    Initialisiert die Datenbank.
    """
    init_db()


# --- SQL-Generierung mit OpenAI GPT ---

def generate_sql_query(user_message: str) -> str:
    """
    Generiert aus einer Nutzereingabe eine SQL-SELECT-Query über GPT-4o-mini.
    Erlaubt nur SELECT, keine destruktiven SQL-Befehle.

    :param user_message: Freitext des Nutzers
    :return: SQL-Query als String
    """
    prompt = [
        {
            "role": "system",
            "content": """
Du bist ein SQL-Experte. Deine Aufgabe ist es, Nutzereingaben in SQL-SELECT-Statements umzuwandeln.
⚠️ Vermeide alle DELETE, UPDATE, INSERT, DROP, ALTER oder andere destruktive SQL-Befehle.
✅ Erlaube nur SELECT-Statements mit WHERE, ORDER BY oder GROUP BY.
Antworte ausschließlich mit der SQL-Query, ohne Erklärung oder Formatierung.
"""
        },
        {
            "role": "user",
            "content": user_message
        }
    ]

    response = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=prompt,
        temperature=0,
        max_tokens=150
    )

    return response.choices[0].message.content.strip()


def is_safe_sql_query(query: str) -> bool:
    """
    Prüft, ob eine SQL-Query sicher ist (keine destruktiven Befehle enthält).

    :param query: SQL-Query als String
    :return: True wenn sicher, sonst False
    """
    cleaned = query.strip().lower()
    # Query muss mit SELECT beginnen
    if not cleaned.startswith("select"):
        return False
    # Verbote für gefährliche SQL-Befehle
    unsafe_keywords = ["delete", "drop", "update", "insert", "alter", "truncate"]
    for keyword in unsafe_keywords:
        if re.search(rf"\b{keyword}\b", cleaned):
            return False
    return True


def results_to_html_table(results):
    """
    Wandelt SQL-Ergebnis (Liste von Zeilen) in eine HTML-Tabelle um.

    :param results: Liste von Ergebnissen (RowProxy-Objekte)
    :return: HTML-String mit Tabelle
    """
    if not results:
        return "<p>Keine Ergebnisse gefunden.</p>"

    columns = results[0].keys()  # <-- hier geändert
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


# ----- CRUD-ENDPOINTS FÜR ENTITIES -----
# SALES

class SaleSchema(BaseModel):
    id: int
    customer_id: int
    product_id: int
    quantity: int
    total_amount: float
    sale_date: date
    city: str

    class Config:
        orm_mode = True


class SaleCreateSchema(BaseModel):
    customer_id: int
    product_id: int
    quantity: int
    total_amount: float
    sale_date: date
    city: str

    class Config:
        orm_mode = True


@app.get("/sales", response_model=List[SaleSchema])
def read_sales(db: Session = Depends(get_db)):
    """
    Alle Sales-Datensätze lesen
    """
    return db.query(Sale).all()


@app.post("/sales", response_model=SaleSchema, status_code=201)
def create_sale(sale: SaleCreateSchema, db: Session = Depends(get_db)):
    """
    Neuen Sale anlegen
    """
    db_sale = Sale(**sale.dict())
    db.add(db_sale)
    db.commit()
    db.refresh(db_sale)
    return db_sale


@app.put("/sales/{sale_id}", response_model=SaleSchema)
def update_sale(sale_id: int, updated_sale: SaleCreateSchema, db: Session = Depends(get_db)):
    """
    Sale aktualisieren
    """
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
    """
    Sale löschen
    """
    sale = db.query(Sale).filter(Sale.id == sale_id).first()
    if not sale:
        raise HTTPException(status_code=404, detail="Sale not found")
    db.delete(sale)
    db.commit()
    return


# CUSTOMERS

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


@app.get("/customers", response_model=List[CustomerSchema])
def read_customers(db: Session = Depends(get_db)):
    """
    Alle Kunden lesen
    """
    return db.query(Customer).all()


@app.post("/customers", response_model=CustomerSchema, status_code=201)
def create_customer(customer: CustomerCreateSchema, db: Session = Depends(get_db)):
    """
    Neuen Kunden anlegen
    """
    db_customer = Customer(**customer.dict())
    db.add(db_customer)
    db.commit()
    db.refresh(db_customer)
    return db_customer


@app.put("/customers/{customer_id}", response_model=CustomerSchema)
def update_customer(customer_id: int, updated_customer: CustomerCreateSchema, db: Session = Depends(get_db)):
    """
    Kunden aktualisieren
    """
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
    """
    Kunden löschen
    """
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    db.delete(customer)
    db.commit()
    return


# PRODUCTS

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


@app.get("/products", response_model=List[ProductSchema])
def read_products(db: Session = Depends(get_db)):
    """
    Alle Produkte lesen
    """
    return db.query(Product).all()


@app.post("/products", response_model=ProductSchema, status_code=201)
def create_product(product: ProductCreateSchema, db: Session = Depends(get_db)):
    """
    Neues Produkt anlegen
    """
    db_product = Product(**product.dict())
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product


@app.put("/products/{product_id}", response_model=ProductSchema)
def update_product(product_id: int, updated_product: ProductCreateSchema, db: Session = Depends(get_db)):
    """
    Produkt aktualisieren
    """
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
    """
    Produkt löschen
    """
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    db.delete(product)
    db.commit()
    return


# EMPLOYEES

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


@app.get("/employees", response_model=List[EmployeeSchema])
def read_employees(db: Session = Depends(get_db)):
    """
    Alle Mitarbeiter lesen
    """
    return db.query(Employee).all()


@app.post("/employees", response_model=EmployeeSchema, status_code=201)
def create_employee(employee: EmployeeCreateSchema, db: Session = Depends(get_db)):
    """
    Neuen Mitarbeiter anlegen
    """
    db_employee = Employee(**employee.dict())
    db.add(db_employee)
    db.commit()
    db.refresh(db_employee)
    return db_employee


@app.put("/employees/{employee_id}", response_model=EmployeeSchema)
def update_employee(employee_id: int, updated_employee: EmployeeCreateSchema, db: Session = Depends(get_db)):
    """
    Mitarbeiter aktualisieren
    """
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
    """
    Mitarbeiter löschen
    """
    employee = db.query(Employee).filter(Employee.id == employee_id).first()
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    db.delete(employee)
    db.commit()
    return


# GENERIERTE TEXTE (ChatGPT)

@app.post("/texts", response_model=GeneratedTextResponse, status_code=201)
def create_generated_text(text_create: GeneratedTextCreate, db: Session = Depends(get_db)):
    """
    Neuen generierten Text speichern
    """
    db_text = GeneratedText(**text_create.dict())
    db.add(db_text)
    db.commit()
    db.refresh(db_text)
    return db_text


@app.get("/texts", response_model=List[GeneratedTextResponse])
def read_generated_texts(db: Session = Depends(get_db)):
    """
    Alle generierten Texte lesen
    """
    return db.query(GeneratedText).all()


# CHAT-ENDPOINT, der SQL-Query generiert und ausführt

class ChatRequest(BaseModel):
    message: str


class ChatResponse(BaseModel):
    response: str


@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest, db: Session = Depends(get_db)):
    user_message = request.message.strip()
    if not user_message:
        raise HTTPException(status_code=422, detail="Nachricht darf nicht leer sein")

    try:
        sql_query = generate_sql_query(user_message)

        if not is_safe_sql_query(sql_query):
            return {"response": "Achtung: Die generierte SQL-Query ist potenziell gefährlich"}

        results_proxy = db.execute(text(sql_query))

        columns = results_proxy.keys()
        results = [dict(zip(columns, row)) for row in results_proxy]

        html_table = results_to_html_table(results)

        return {"response": html_table}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



