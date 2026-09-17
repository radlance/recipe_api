import logging
import os

from app.database import SessionLocal
from app.models import Ingredient, Recipe

logger = logging.getLogger(__name__)

INITIAL_RECIPES = [
    {
        "recipe": {
            "title": "Блины классические",
            "description": "Тонкие аппетитные блины на молоке со сливочным маслом",
            "cooking_time_minutes": 30,
            "difficulty": 2,
            "category": "breakfast",
        },
        "ingredients": [
            {"name": "Мука пшеничная", "quantity": 200.0, "unit": "g"},
            {"name": "Молоко 3.2%", "quantity": 500.0, "unit": "ml"},
            {"name": "Яйца куриные", "quantity": 2.0, "unit": "pcs"},
            {"name": "Сахар", "quantity": 2.0, "unit": "tbsp"},
            {"name": "Масло сливочное", "quantity": 30.0, "unit": "g"},
        ],
    },
    {
        "recipe": {
            "title": "Паста Карбонара",
            "description": "Традиционная итальянская паста с хрустящим беконом и сливочно-сырным соусом",
            "cooking_time_minutes": 25,
            "difficulty": 3,
            "category": "dinner",
        },
        "ingredients": [
            {"name": "Спагетти", "quantity": 300.0, "unit": "g"},
            {"name": "Бекон", "quantity": 150.0, "unit": "g"},
            {"name": "Сыр Пармезан", "quantity": 50.0, "unit": "g"},
            {"name": "Сливки 20%", "quantity": 100.0, "unit": "ml"},
            {"name": "Яичные желтки", "quantity": 3.0, "unit": "pcs"},
        ],
    },
    {
        "recipe": {
            "title": "Овощной салат с оливками",
            "description": "Свежий и легкий салат из сезонных овощей с оливковым маслом",
            "cooking_time_minutes": 15,
            "difficulty": 1,
            "category": "lunch",
        },
        "ingredients": [
            {"name": "Помидоры", "quantity": 3.0, "unit": "pcs"},
            {"name": "Огурцы", "quantity": 2.0, "unit": "pcs"},
            {"name": "Масло оливковое", "quantity": 2.0, "unit": "tbsp"},
            {"name": "Соль морская", "quantity": 1.0, "unit": "tsp"},
        ],
    },
]


def seed_initial_data() -> None:
    """Populate database with initial recipes and ingredients if empty."""
    if os.getenv("TESTING", "false").lower() in ("true", "1", "yes"):
        return

    db = SessionLocal()
    try:
        if db.query(Recipe).first() is not None:
            return

        for item in INITIAL_RECIPES:
            recipe = Recipe(**item["recipe"])
            db.add(recipe)
            db.flush()

            for ing_data in item["ingredients"]:
                ingredient = Ingredient(recipe_id=recipe.id, **ing_data)
                db.add(ingredient)

        db.commit()
    except Exception as exc:
        db.rollback()
        logger.warning("Failed to seed initial data: %s", exc)
    finally:
        db.close()
