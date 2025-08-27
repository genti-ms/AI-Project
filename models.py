# Update-Test: 27.08.2025
from sqlalchemy import Column, Integer, String, Float, Date, ForeignKey, DateTime, Text
from sqlalchemy.orm import relationship, backref
from sqlalchemy.types import JSON
from datetime import datetime
from database import Base


class GeneratedText(Base):
    __tablename__ = "generated_texts"

    id = Column(Integer, primary_key=True, index=True)
    prompt = Column(Text, nullable=False)
    summary = Column(Text, nullable=False)
    key_points = Column(JSON, nullable=False)
    sentiment = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)


class Customer(Base):
    __tablename__ = "customers"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    email = Column(String, nullable=False, unique=True)
    city = Column(String, nullable=False)
    country = Column(String, nullable=False)

    sales = relationship("Sale", back_populates="customer", cascade="all, delete-orphan")


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    price = Column(Float, nullable=False, default=0.0)
    stock = Column(Integer, nullable=False, default=0)

    sales = relationship("Sale", back_populates="product", cascade="all, delete-orphan")


class Employee(Base):
    __tablename__ = "employees"

    id = Column(Integer, primary_key=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    email = Column(String, nullable=False, unique=True)
    position = Column(String, nullable=False)

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

    # Bidirektionale Relationships
    customer = relationship("Customer", back_populates="sales", lazy="joined")
    product = relationship("Product", back_populates="sales", lazy="joined")
    employee = relationship("Employee", back_populates="sales", lazy="joined")
