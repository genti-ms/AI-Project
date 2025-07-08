from fastapi import FastAPI, Depends, Body, HTTPException
from sqlalchemy.orm import Session
from typing import List
from pydantic import BaseModel
from datetime import date
from dotenv import load_dotenv
import os
import openai

from database import SessionLocal, engine
from models import Base, Sale, Customer, Product, Employee

load_dotenv()

openai_api_key = os.getenv("OPENAI_API_KEY")
if not openai_api_key:
    raise ValueError("OpenAI API key not found in environment variables")

openai.api_key = openai_api_key

app = FastAPI()

def init_db():
    """
    Initialize the database by creating all tables.
    """
    Base.metadata.create_all(bind=engine)

def get_db():
    """
    Provide a database session to path operations.

    Yields:
        Session: SQLAlchemy database session.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.on_event("startup")
def on_startup():
    """
    Event handler for application startup.
    Initializes the database schema.
    """
    init_db()

# --- SALES ---
class SaleSchema(BaseModel):
    id: int
    customer_id: int
    product_id: int
    quantity: int
    total_amount: float
    sale_date: date
    city: str

    model_config = {"from_attributes": True}

class SaleCreateSchema(BaseModel):
    customer_id: int
    product_id: int
    quantity: int
    total_amount: float
    sale_date: date
    city: str

    model_config = {"from_attributes": True}

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

# --- CUSTOMERS ---
class CustomerSchema(BaseModel):
    id: int
    name: str
    email: str
    city: str
    country: str

    model_config = {"from_attributes": True}

class CustomerCreateSchema(BaseModel):
    name: str
    email: str
    city: str
    country: str

    model_config = {"from_attributes": True}

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

# --- PRODUCTS ---
class ProductSchema(BaseModel):
    id: int
    name: str
    description: str
    price: float
    stock: int

    model_config = {"from_attributes": True}

class ProductCreateSchema(BaseModel):
    name: str
    description: str
    price: float
    stock: int

    model_config = {"from_attributes": True}

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

# --- EMPLOYEES ---
class EmployeeSchema(BaseModel):
    id: int
    first_name: str
    last_name: str
    email: str
    position: str

    model_config = {"from_attributes": True}

class EmployeeCreateSchema(BaseModel):
    first_name: str
    last_name: str
    email: str
    position: str

    model_config = {"from_attributes": True}

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

# --- OPENAI INTEGRATION ---

class PromptRequest(BaseModel):
    prompt: str

@app.post("/generate-text")
async def generate_text(request: PromptRequest = Body(...)):
    if not request.prompt.strip():
        raise HTTPException(status_code=422, detail="Prompt cant be empty")

    if not openai.api_key:
        raise HTTPException(status_code=500, detail="OpenAI API key not configured")

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": request.prompt}
            ],
            max_tokens=150,
        )
        generated_text = response.choices[0].message.content
        return {"generated_text": generated_text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
