# Letzte bearbeitung 30.08
from sqlalchemy import Column, Integer, String, Float, Date, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base

class Customer(Base):
    __tablename__ = "customers"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    email = Column(String, nullable=False, unique=True)
    city = Column(String, nullable=False)
    country = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)

    sales = relationship("Sale", back_populates="customer", cascade="all, delete-orphan")

class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    category = Column(String, nullable=True)
    price = Column(Float, nullable=False, default=0.0)
    stock = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)

    sales = relationship("Sale", back_populates="product", cascade="all, delete-orphan")

class Employee(Base):
    __tablename__ = "employees"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    region = Column(String, nullable=True)
    hire_date = Column(DateTime, default=datetime.utcnow, index=True)

    sales = relationship("Sale", back_populates="employee", cascade="all, delete-orphan")

class Sale(Base):
    __tablename__ = "sales"

    id = Column(Integer, primary_key=True)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    employee_id = Column(Integer, ForeignKey("employees.id"), nullable=False)
    quantity = Column(Integer, nullable=False, default=1)
    total_amount = Column(Float, nullable=False, default=0.0)
    sale_date = Column(Date, nullable=False, default=datetime.utcnow)
    city = Column(String, nullable=False)

    customer = relationship("Customer", back_populates="sales", lazy="joined")
    product = relationship("Product", back_populates="sales", lazy="joined")
    employee = relationship("Employee", back_populates="sales", lazy="joined")
