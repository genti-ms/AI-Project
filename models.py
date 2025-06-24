from sqlalchemy import Column, Integer, String, Float, Date, ForeignKey
from sqlalchemy.orm import relationship
from database import Base

class Customer(Base):
    __tablename__ = "customers"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    email = Column(String)
    city = Column(String)
    country = Column(String)

class Product(Base):
    __tablename__ = "products"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    description = Column(String)
    price = Column(Float)
    stock = Column(Integer)

class Employee(Base):
    __tablename__ = "employees"
    id = Column(Integer, primary_key=True)
    first_name = Column(String)
    last_name = Column(String)
    email = Column(String)
    position = Column(String)

class Sale(Base):
    __tablename__ = "sales"
    id = Column(Integer, primary_key=True)
    customer_id = Column(Integer, ForeignKey("customers.id"))
    product_id = Column(Integer, ForeignKey("products.id"))
    employee_id = Column(Integer, ForeignKey("employees.id"))

    quantity = Column(Integer)
    total_amount = Column(Float)
    sale_date = Column(Date)
    city = Column(String)

    customer = relationship("Customer")
    product = relationship("Product")
    employee = relationship("Employee")
