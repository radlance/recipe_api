from typing import Annotated

from fastapi import APIRouter, Depends, Response
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Recipe
from app.schemas import (
    ErrorResponse,
    RecipeCreateRequest,
    RecipeDetailSingleResponse,
    RecipeListResponse,
    RecipeSingleResponse,
    RecipeUpdateRequest,
)

router = APIRouter(prefix="/api/recipes", tags=["recipes"])

DbSession = Annotated[Session, Depends(get_db)]


@router.get(
    "",
    response_model=RecipeListResponse,
    summary="Получить список всех рецептов",
    description='Возвращает список всех зарегистрированных рецептов в виде JSON: `{"list": [...]}`.',
    response_description="Список всех рецептов",
)
def get_recipes(db: DbSession):
    """Return a list of all recipes."""
    recipes = db.query(Recipe).all()
    return {"list": recipes}


@router.get(
    "/{recipe_id}",
    response_model=RecipeDetailSingleResponse,
    responses={404: {"model": ErrorResponse, "description": "Рецепт не найден"}},
    summary="Получить рецепт по ID с ингредиентами",
    description="Возвращает карточку конкретного рецепта с вложенным массивом всех связанных ингредиентов.",
    response_description="Найденный рецепт с ингредиентами",
)
def get_recipe(recipe_id: int, db: DbSession):
    """Return a single recipe by id, including its ingredients."""
    recipe = db.query(Recipe).filter(Recipe.id == recipe_id).first()
    if not recipe:
        return JSONResponse(
            status_code=404,
            content={"status": 404, "reason": "Recipe not found"},
        )
    return {"recipe": recipe}


@router.post(
    "",
    response_model=RecipeSingleResponse,
    responses={
        400: {"model": ErrorResponse, "description": "Ошибка валидации полей"},
        500: {"model": ErrorResponse, "description": "Ошибка сервера при сохранении"},
    },
    summary="Создать новый рецепт",
    description='Создает новый рецепт. В теле запроса ожидается JSON вида `{"recipe": {...}}` со всеми обязательными полями.',
    response_description="Успешно созданный рецепт с присвоенным ID",
)
def create_recipe(payload: RecipeCreateRequest, db: DbSession):
    """Create a new recipe."""
    try:
        recipe = Recipe(**payload.recipe.model_dump())
        db.add(recipe)
        db.commit()
        db.refresh(recipe)
        return {"recipe": recipe}
    except SQLAlchemyError as exc:
        db.rollback()
        return JSONResponse(
            status_code=500,
            content={"status": 500, "reason": str(exc)},
        )


@router.patch(
    "/{recipe_id}",
    response_model=RecipeSingleResponse,
    responses={
        400: {"model": ErrorResponse, "description": "Недопустимые значения полей"},
        404: {"model": ErrorResponse, "description": "Рецепт не найден"},
        500: {"model": ErrorResponse, "description": "Внутренняя ошибка сервера"},
    },
    summary="Частично обновить рецепт (PATCH)",
    description="Обновляет переданные атрибуты рецепта. Все поля в объекте `recipe` являются необязательными.",
    response_description="Обновленный рецепт",
)
def update_recipe(
    recipe_id: int,
    payload: RecipeUpdateRequest,
    db: DbSession,
):
    """Partially update a recipe by id."""
    recipe = db.query(Recipe).filter(Recipe.id == recipe_id).first()
    if not recipe:
        return JSONResponse(
            status_code=404,
            content={"status": 404, "reason": "Recipe not found"},
        )

    try:
        update_data = payload.recipe.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(recipe, key, value)
        db.commit()
        db.refresh(recipe)
        return {"recipe": recipe}
    except SQLAlchemyError as exc:
        db.rollback()
        return JSONResponse(
            status_code=500,
            content={"status": 500, "reason": str(exc)},
        )


@router.delete(
    "/{recipe_id}",
    status_code=202,
    responses={
        202: {"description": "Запрос на удаление принят (успех)"},
        404: {"model": ErrorResponse, "description": "Рецепт не найден"},
        500: {"model": ErrorResponse, "description": "Внутренняя ошибка сервера"},
    },
    summary="Удалить рецепт (каскадное удаление)",
    description="Удаляет рецепт по ID. Все связанные ингредиенты удаляются автоматически (CASCADE). По ТЗ возвращает статус 202 Accepted.",
    response_description="Подтверждение удаления",
)
def delete_recipe(recipe_id: int, db: DbSession):
    """Delete a recipe by id (cascades to ingredients)."""
    recipe = db.query(Recipe).filter(Recipe.id == recipe_id).first()
    if not recipe:
        return JSONResponse(
            status_code=404,
            content={"status": 404, "reason": "Recipe not found"},
        )

    try:
        db.delete(recipe)
        db.commit()
        return Response(status_code=202)
    except SQLAlchemyError as exc:
        db.rollback()
        return JSONResponse(
            status_code=500,
            content={"status": 500, "reason": str(exc)},
        )
