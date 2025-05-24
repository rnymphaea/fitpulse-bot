from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship, declarative_base
from sqlalchemy.sql import func
from datetime import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    telegram_id = Column(Integer, unique=True, nullable=False)
    username = Column(String(32))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    products = relationship("Product", back_populates="user")
    meals = relationship("Meal", back_populates="user")


class Product(Base):
    __tablename__ = 'products'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    name = Column(String(100), unique=True, nullable=False)
    calories = Column(Integer, nullable=False)
    protein = Column(Integer, nullable=False)
    fats = Column(Integer, nullable=False)
    carbs = Column(Integer, nullable=False)
    category_id = Column(Integer, ForeignKey('categories.id'))

    user = relationship("User", back_populates='products')
    category = relationship("Category", back_populates='product')


class Category(Base):
    __tablename__ = 'categories'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True, nullable=False)

    product = relationship("Product", back_populates='category')


class Meal(Base):
    __tablename__ = 'meals'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    type_id = Column(Integer, ForeignKey('meal_types.id'), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    user = relationship("User", back_populates="meals")
    products = relationship("MealItem", back_populates="meal")
    type = relationship("MealType")


class MealType(Base):
    __tablename__ = 'meal_types'

    id = Column(Integer, primary_key=True)
    name = Column(String(15), unique=True, nullable=False)


class MealItem(Base):
    __tablename__ = 'meal_items'
    
    meal_id = Column(Integer, ForeignKey('meals.id'), primary_key=True)
    product_id = Column(Integer, ForeignKey('products.id'), primary_key=True)
    quantity = Column(Integer, nullable=False)
    
    meal = relationship("Meal", back_populates="products")
    product = relationship("Product")

