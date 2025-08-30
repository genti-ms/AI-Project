from database import SessionLocal
from models import Customer, Product, Employee, Sale
from datetime import datetime, timedelta, date
from decimal import Decimal
import random
from contextlib import contextmanager

@contextmanager
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_entries(db, model_class, data_list):
    for entry in data_list:
        db.add(model_class(**entry))

# Zufällige Zeitgeneratoren
def random_past_date(days=90):
    return datetime.utcnow() - timedelta(days=random.randint(0, days))

# Kunden
customers = [
    {"name": "Hans Johannesen", "email": "hj1@example.com", "city": "Berlin", "country": "Germany"},
    {"name": "Anna Müller", "email": "anna.mueller@example.com", "city": "Munich", "country": "Germany"},
    # ... weitere Kunden
]

for c in customers:
    c["created_at"] = random_past_date(180)  # zufällige letzten 6 Monate

# Produkte
products = [
    {"name": "Laptop Pro 15", "category": "Laptops", "price": Decimal("1499.99"), "stock": 25},
    {"name": "Smartphone X", "category": "Smartphones", "price": Decimal("999.99"), "stock": 50},
    # ... weitere Produkte
]

for p in products:
    p["created_at"] = random_past_date(180)

# Mitarbeiter
employees = [
    {"name": "Michael Schneider", "region": "North"},
    {"name": "Laura Hartmann", "region": "South"},
    # ... weitere Mitarbeiter
]

for e in employees:
    e["hire_date"] = random_past_date(365)  # innerhalb des letzten Jahres

# Verkäufe, garantiert mindestens 1 pro Monat
def generate_sales(num_sales_per_month=3, start_month=1, end_month=6):
    sales = []
    for month in range(start_month, end_month + 1):
        for i in range(num_sales_per_month):
            quantity = random.randint(1, 5)
            product_index = i % len(products)
            price = products[product_index]["price"]
            total_amount = float(price) * quantity
            customer = customers[i % len(customers)]
            employee = employees[i % len(employees)]
            sale_day = random.randint(1, 28)
            sales.append({
                "customer_id": (i % len(customers)) + 1,
                "product_id": (i % len(products)) + 1,
                "employee_id": (i % len(employees)) + 1,
                "quantity": quantity,
                "total_amount": total_amount,
                "sale_date": date(2025, month, sale_day),
                "city": customer["city"],
            })
    return sales

def seed():
    with get_db() as db:
        if db.query(Customer).first() is None:
            create_entries(db, Customer, customers)
        if db.query(Product).first() is None:
            create_entries(db, Product, products)
        if db.query(Employee).first() is None:
            create_entries(db, Employee, employees)
        if db.query(Sale).first() is None:
            create_entries(db, Sale, generate_sales())
        db.commit()

if __name__ == "__main__":
    seed()
    print("✅ Database successfully seeded with test data.")
