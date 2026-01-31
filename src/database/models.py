"""
SQLAlchemy ORM models for WhatCanICook database.
Defines Python classes that map to database tables.
"""

from sqlalchemy import create_engine, Column, Integer, Text, ForeignKey, Table, CheckConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from datetime import datetime
from pathlib import Path

# Database path
DB_PATH = Path(__file__).parent.parent / "whatcanicook.db"
DATABASE_URL = f"sqlite:///{DB_PATH}"

# Create base class for models
Base = declarative_base()


class Recipe(Base):
    """Recipe model - stores recipe metadata"""
    __tablename__ = 'recipes'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(Text, nullable=False)
    description = Column(Text)
    cook_time_mins = Column(Integer)
    source_url = Column(Text)
    created_at = Column(Text, default=datetime.utcnow)
    
    # Relationships
    ingredients = relationship("RecipeIngredient", back_populates="recipe", cascade="all, delete-orphan")
    tags = relationship("RecipeTag", back_populates="recipe", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Recipe(id={self.id}, name='{self.name}', cook_time={self.cook_time_mins})>"


class Ingredient(Base):
    """Ingredient model - master list of ingredients"""
    __tablename__ = 'ingredients'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(Text, unique=True, nullable=False)
    is_staple = Column(Integer, default=0)
    
    # Relationships
    recipes = relationship("RecipeIngredient", back_populates="ingredient")
    
    __table_args__ = (
        CheckConstraint('is_staple IN (0, 1)', name='check_is_staple'),
    )
    
    def __repr__(self):
        staple_str = "staple" if self.is_staple else "non-staple"
        return f"<Ingredient(id={self.id}, name='{self.name}', {staple_str})>"


class RecipeIngredient(Base):
    """Junction table - links recipes to ingredients"""
    __tablename__ = 'recipe_ingredients'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    recipe_id = Column(Integer, ForeignKey('recipes.id', ondelete='CASCADE'), nullable=False)
    ingredient_id = Column(Integer, ForeignKey('ingredients.id', ondelete='CASCADE'), nullable=False)
    quantity = Column(Text)
    unit = Column(Text)
    
    # Relationships
    recipe = relationship("Recipe", back_populates="ingredients")
    ingredient = relationship("Ingredient", back_populates="recipes")
    
    def __repr__(self):
        return f"<RecipeIngredient(recipe_id={self.recipe_id}, ingredient_id={self.ingredient_id})>"


class Tag(Base):
    """Tag model - categorization tags"""
    __tablename__ = 'tags'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(Text, unique=True, nullable=False)
    category = Column(Text)
    
    # Relationships
    recipes = relationship("RecipeTag", back_populates="tag")
    
    def __repr__(self):
        return f"<Tag(id={self.id}, name='{self.name}', category='{self.category}')>"


class RecipeTag(Base):
    """Junction table - links recipes to tags"""
    __tablename__ = 'recipe_tags'
    
    recipe_id = Column(Integer, ForeignKey('recipes.id', ondelete='CASCADE'), primary_key=True)
    tag_id = Column(Integer, ForeignKey('tags.id', ondelete='CASCADE'), primary_key=True)
    
    # Relationships
    recipe = relationship("Recipe", back_populates="tags")
    tag = relationship("Tag", back_populates="recipes")
    
    def __repr__(self):
        return f"<RecipeTag(recipe_id={self.recipe_id}, tag_id={self.tag_id})>"


# Database engine and session factory
engine = create_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(bind=engine)


def get_session():
    """Get a database session for queries"""
    return SessionLocal()
