from database import SessionLocal
from models import Customer, Product, Employee, Sale
from datetime import date
from decimal import Decimal
import random

db = SessionLocal()

# --- Customers (20) ---
customers = [
    {"name": "Hans Johannesen", "email": "hj1@example.com", "city": "Berlin", "country": "Germany"},
    {"name": "Anna Müller", "email": "anna.mueller@example.com", "city": "Munich", "country": "Germany"},
    {"name": "Lars Schmidt", "email": "lars.schmidt@example.com", "city": "Hamburg", "country": "Germany"},
    {"name": "Petra Bauer", "email": "petra.bauer@example.com", "city": "Cologne", "country": "Germany"},
    {"name": "Klaus Meier", "email": "klaus.meier@example.com", "city": "Frankfurt", "country": "Germany"},
    {"name": "Monika Fischer", "email": "monika.fischer@example.com", "city": "Stuttgart", "country": "Germany"},
    {"name": "Jan Becker", "email": "jan.becker@example.com", "city": "Dresden", "country": "Germany"},
    {"name": "Sophie Weber", "email": "sophie.weber@example.com", "city": "Leipzig", "country": "Germany"},
    {"name": "Tobias Wolf", "email": "tobias.wolf@example.com", "city": "Dortmund", "country": "Germany"},
    {"name": "Julia Klein", "email": "julia.klein@example.com", "city": "Nuremberg", "country": "Germany"},
    {"name": "Markus Braun", "email": "markus.braun@example.com", "city": "Bremen", "country": "Germany"},
    {"name": "Lisa Hoffmann", "email": "lisa.hoffmann@example.com", "city": "Hanover", "country": "Germany"},
    {"name": "Stefan Richter", "email": "stefan.richter@example.com", "city": "Essen", "country": "Germany"},
    {"name": "Nina Wolf", "email": "nina.wolf@example.com", "city": "Duisburg", "country": "Germany"},
    {"name": "Oliver Klein", "email": "oliver.klein@example.com", "city": "Bochum", "country": "Germany"},
    {"name": "Claudia König", "email": "claudia.koenig@example.com", "city": "Wuppertal", "country": "Germany"},
    {"name": "Michael Lang", "email": "michael.lang@example.com", "city": "Bonn", "country": "Germany"},
    {"name": "Sandra Fuchs", "email": "sandra.fuchs@example.com", "city": "Mannheim", "country": "Germany"},
    {"name": "Peter Weiß", "email": "peter.weiss@example.com", "city": "Karlsruhe", "country": "Germany"},
    {"name": "Julia Neumann", "email": "julia.neumann@example.com", "city": "Wiesbaden", "country": "Germany"},
]

# --- Products (20) ---
products = [
    {"name": "Laptop Pro 15", "description": "High-end laptop", "price": Decimal("1499.99"), "stock": 25},
    {"name": "Smartphone X", "description": "Latest smartphone model", "price": Decimal("999.99"), "stock": 50},
    {"name": "Wireless Mouse", "description": "Ergonomic wireless mouse", "price": Decimal("49.99"), "stock": 150},
    {"name": "Mechanical Keyboard", "description": "RGB backlit keyboard", "price": Decimal("89.99"), "stock": 80},
    {"name": "27\" Monitor", "description": "4K UHD display", "price": Decimal("299.99"), "stock": 40},
    {"name": "USB-C Hub", "description": "Multiport adapter", "price": Decimal("29.99"), "stock": 120},
    {"name": "External SSD 1TB", "description": "Portable SSD drive", "price": Decimal("129.99"), "stock": 60},
    {"name": "Noise Cancelling Headphones", "description": "Wireless over-ear headphones", "price": Decimal("199.99"), "stock": 70},
    {"name": "Smartwatch Series 5", "description": "Fitness tracking watch", "price": Decimal("249.99"), "stock": 35},
    {"name": "Gaming Chair", "description": "Comfortable ergonomic chair", "price": Decimal("159.99"), "stock": 20},
    {"name": "Bluetooth Speaker", "description": "Portable speaker", "price": Decimal("79.99"), "stock": 90},
    {"name": "Webcam HD", "description": "High-definition webcam", "price": Decimal("59.99"), "stock": 100},
    {"name": "Tablet Plus", "description": "10-inch tablet", "price": Decimal("399.99"), "stock": 45},
    {"name": "Wireless Charger", "description": "Fast wireless charger", "price": Decimal("39.99"), "stock": 110},
    {"name": "Fitness Tracker", "description": "Activity tracker wristband", "price": Decimal("99.99"), "stock": 80},
    {"name": "Smart Light Bulb", "description": "WiFi-enabled bulb", "price": Decimal("24.99"), "stock": 150},
    {"name": "Router X2000", "description": "Dual-band router", "price": Decimal("89.99"), "stock": 60},
    {"name": "Action Camera", "description": "4K waterproof camera", "price": Decimal("179.99"), "stock": 40},
    {"name": "E-Reader", "description": "6-inch e-book reader", "price": Decimal("129.99"), "stock": 55},
    {"name": "Gaming Mouse", "description": "High precision mouse", "price": Decimal("69.99"), "stock": 70},
]

# --- Employees (20) ---
employees = [
    {"first_name": "Michael", "last_name": "Schneider", "email": "michael.schneider@example.com", "position": "Sales Manager"},
    {"first_name": "Laura", "last_name": "Hartmann", "email": "laura.hartmann@example.com", "position": "Accountant"},
    {"first_name": "Stefan", "last_name": "Neumann", "email": "stefan.neumann@example.com", "position": "Developer"},
    {"first_name": "Eva", "last_name": "Klein", "email": "eva.klein@example.com", "position": "HR Specialist"},
    {"first_name": "Daniel", "last_name": "Bauer", "email": "daniel.bauer@example.com", "position": "Marketing"},
    {"first_name": "Sarah", "last_name": "Fischer", "email": "sarah.fischer@example.com", "position": "Sales Assistant"},
    {"first_name": "Tom", "last_name": "Wagner", "email": "tom.wagner@example.com", "position": "Customer Support"},
    {"first_name": "Nina", "last_name": "Koch", "email": "nina.koch@example.com", "position": "Designer"},
    {"first_name": "Jan", "last_name": "Zimmermann", "email": "jan.zimmermann@example.com", "position": "Product Manager"},
    {"first_name": "Lena", "last_name": "Wolf", "email": "lena.wolf@example.com", "position": "QA Engineer"},
    {"first_name": "Peter", "last_name": "Schulz", "email": "peter.schulz@example.com", "position": "Sales"},
    {"first_name": "Sandra", "last_name": "Mayer", "email": "sandra.mayer@example.com", "position": "Support"},
    {"first_name": "Karl", "last_name": "Neumann", "email": "karl.neumann@example.com", "position": "Developer"},
    {"first_name": "Anna", "last_name": "Berg", "email": "anna.berg@example.com", "position": "Marketing"},
    {"first_name": "Lukas", "last_name": "Schmidt", "email": "lukas.schmidt@example.com", "position": "Sales"},
    {"first_name": "Jana", "last_name": "Fischer", "email": "jana.fischer@example.com", "position": "HR"},
    {"first_name": "Tobias", "last_name": "Weber", "email": "tobias.weber@example.com", "position": "Product Owner"},
    {"first_name": "Isabel", "last_name": "Krause", "email": "isabel.krause@example.com", "position": "Designer"},
    {"first_name": "Jan", "last_name": "Lorenz", "email": "jan.lorenz@example.com", "position": "QA"},
    {"first_name": "Miriam", "last_name": "Hoffmann", "email": "miriam.hoffmann@example.com", "position": "Customer Support"},
]

# --- Sales (20) ---
sales = []
for i in range(20):
    customer_id = (i % 20) + 1  # IDs 1-20 cycling
    product_id = random.randint(1, 20)
    quantity = random.randint(1, 5)
    product_price = products[product_id - 1]["price"]
    total_amount = product_price * quantity
    sale_date = date(2025, random.randint(1, 6), random.randint(1, 28))
    city = customers[customer_id - 1]["city"]
    sales.append({
        "customer_id": customer_id,
        "product_id": product_id,
        "quantity": quantity,
        "total_amount": total_amount,
        "sale_date": sale_date,
        "city": city,
    })

def seed():
    # Insert Customers
    for c in customers:
        db_customer = Customer(**c)
        db.add(db_customer)

    # Insert Products
    for p in products:
        db_product = Product(**p)
        db.add(db_product)

    # Insert Employees
    for e in employees:
        db_employee = Employee(**e)
        db.add(db_employee)

    db.commit()

    # Insert Sales (after committing customers and products)
    for s in sales:
        db_sale = Sale(**s)
        db.add(db_sale)

    db.commit()

if __name__ == "__main__":
    seed()
    print("Database seeded with 20 entries for Customers, Products, Employees, and Sales.")
