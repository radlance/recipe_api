from sqlalchemy import Column, Float, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.database import Base


class Recipe(Base):
    """SQLAlchemy model for the recipes table."""

    __tablename__ = "recipes"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(100), nullable=False)
    description = Column(String(500), nullable=False)
    cooking_time_minutes = Column(Integer, nullable=False)
    difficulty = Column(Integer, nullable=False)
    category = Column(String(20), nullable=False)

    ingredients = relationship(
        "Ingredient",
        back_populates="recipe",
        cascade="all, delete-orphan",
    )


class Ingredient(Base):
    """SQLAlchemy model for the ingredients table."""

    __tablename__ = "ingredients"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    quantity = Column(Float, nullable=False)
    unit = Column(String(10), nullable=False)
    recipe_id = Column(Integer, ForeignKey("recipes.id", ondelete="CASCADE"), nullable=False)

    recipe = relationship("Recipe", back_populates="ingredients")
