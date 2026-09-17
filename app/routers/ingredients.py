from typing import Annotated

from fastapi import APIRouter, Depends, Response
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Ingredient, Recipe
from app.schemas import (
    ErrorResponse,
    IngredientCreateRequest,
    IngredientListResponse,
    IngredientSingleResponse,
    IngredientUpdateRequest,
)

router = APIRouter(prefix="/api/ingredients", tags=["ingredients"])

DbSession = Annotated[Session, Depends(get_db)]


@router.get(
    "",
    response_model=IngredientListResponse,
    summary="Получить список всех ингредиентов",
    description='Возвращает список всех существующих ингредиентов в виде `{"list": [...]}`.',
    response_description="Список ингредиентов",
)
def get_ingredients(db: DbSession):
    """Return a list of all ingredients."""
    ingredients = db.query(Ingredient).all()
    return {"list": ingredients}


@router.get(
    "/{ingredient_id}",
    response_model=IngredientSingleResponse,
    responses={404: {"model": ErrorResponse, "description": "Ингредиент не найден"}},
    summary="Получить ингредиент по ID",
    description="Возвращает детальную информацию об ингредиенте по его уникальному ID.",
    response_description="Найденный ингредиент",
)
def get_ingredient(ingredient_id: int, db: DbSession):
    """Return a single ingredient by id."""
    ingredient = db.query(Ingredient).filter(Ingredient.id == ingredient_id).first()
    if not ingredient:
        return JSONResponse(
            status_code=404,
            content={"status": 404, "reason": "Ingredient not found"},
        )
    return {"ingredient": ingredient}


@router.post(
    "",
    response_model=IngredientSingleResponse,
    responses={
        400: {
            "model": ErrorResponse,
            "description": "Ошибка валидации или recipe_id не найден",
        },
        500: {"model": ErrorResponse, "description": "Ошибка сервера при создании"},
    },
    summary="Создать новый ингредиент",
    description="Добавляет ингредиент с обязательной привязкой к существующему рецепту через `recipe_id`.",
    response_description="Созданный ингредиент с ID",
)
def create_ingredient(payload: IngredientCreateRequest, db: DbSession):
    """Create a new ingredient."""
    # Check that the referenced recipe exists
    recipe = db.query(Recipe).filter(Recipe.id == payload.ingredient.recipe_id).first()
    if not recipe:
        rec_id = payload.ingredient.recipe_id
        return JSONResponse(
            status_code=400,
            content={
                "status": 400,
                "reason": f"Recipe with id={rec_id} does not exist",
            },
        )

    try:
        ingredient = Ingredient(**payload.ingredient.model_dump())
        db.add(ingredient)
        db.commit()
        db.refresh(ingredient)
        return {"ingredient": ingredient}
    except SQLAlchemyError as exc:
        db.rollback()
        return JSONResponse(
            status_code=500,
            content={"status": 500, "reason": str(exc)},
        )


@router.patch(
    "/{ingredient_id}",
    response_model=IngredientSingleResponse,
    responses={
        400: {
            "model": ErrorResponse,
            "description": "Ошибка валидации или несуществующий recipe_id",
        },
        404: {"model": ErrorResponse, "description": "Ингредиент не найден"},
        500: {"model": ErrorResponse, "description": "Ошибка сервера"},
    },
    summary="Частично обновить ингредиент (PATCH)",
    description="Обновляет отдельные поля ингредиента. Если передан новый `recipe_id`, проверяется существование рецепта в базе.",
    response_description="Обновленный ингредиент",
)
def update_ingredient(
    ingredient_id: int,
    payload: IngredientUpdateRequest,
    db: DbSession,
):
    """Partially update an ingredient by id."""
    ingredient = db.query(Ingredient).filter(Ingredient.id == ingredient_id).first()
    if not ingredient:
        return JSONResponse(
            status_code=404,
            content={"status": 404, "reason": "Ingredient not found"},
        )

    update_data = payload.ingredient.model_dump(exclude_unset=True)

    # If recipe_id is being changed, verify the new recipe exists
    if "recipe_id" in update_data and update_data["recipe_id"] is not None:
        recipe = db.query(Recipe).filter(Recipe.id == update_data["recipe_id"]).first()
        if not recipe:
            rec_id = update_data["recipe_id"]
            return JSONResponse(
                status_code=400,
                content={
                    "status": 400,
                    "reason": f"Recipe with id={rec_id} does not exist",
                },
            )

    try:
        for key, value in update_data.items():
            setattr(ingredient, key, value)
        db.commit()
        db.refresh(ingredient)
        return {"ingredient": ingredient}
    except SQLAlchemyError as exc:
        db.rollback()
        return JSONResponse(
            status_code=500,
            content={"status": 500, "reason": str(exc)},
        )


@router.delete(
    "/{ingredient_id}",
    status_code=202,
    responses={
        202: {"description": "Успешно удалено"},
        404: {"model": ErrorResponse, "description": "Ингредиент не найден"},
        500: {"model": ErrorResponse, "description": "Ошибка сервера"},
    },
    summary="Удалить ингредиент",
    description="Удаляет ингредиент по ID. Возвращает статус 202 Accepted по ТЗ.",
    response_description="Подтверждение удаления",
)
def delete_ingredient(ingredient_id: int, db: DbSession):
    """Delete an ingredient by id."""
    ingredient = db.query(Ingredient).filter(Ingredient.id == ingredient_id).first()
    if not ingredient:
        return JSONResponse(
            status_code=404,
            content={"status": 404, "reason": "Ingredient not found"},
        )

    try:
        db.delete(ingredient)
        db.commit()
        return Response(status_code=202)
    except SQLAlchemyError as exc:
        db.rollback()
        return JSONResponse(
            status_code=500,
            content={"status": 500, "reason": str(exc)},
        )
