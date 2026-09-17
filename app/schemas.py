from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field

# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------


class CategoryEnum(str, Enum):
    """Категория блюда."""

    breakfast = "breakfast"
    lunch = "lunch"
    dinner = "dinner"
    dessert = "dessert"
    snack = "snack"


class UnitEnum(str, Enum):
    """Единица измерения ингредиента."""

    g = "g"
    kg = "kg"
    ml = "ml"
    l = "l"
    pcs = "pcs"
    tbsp = "tbsp"
    tsp = "tsp"


# ---------------------------------------------------------------------------
# Recipe Schemas
# ---------------------------------------------------------------------------


class RecipeBase(BaseModel):
    """Базовые поля рецепта."""

    title: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Название блюда (строка до 100 символов)",
        examples=["Классические блины"],
    )
    description: str = Field(
        ...,
        min_length=1,
        max_length=500,
        description="Подробный рецепт или описание приготовления (до 500 символов)",
        examples=["Тонкие русские блины на молоке с добавлением сливочного масла"],
    )
    cooking_time_minutes: int = Field(
        ...,
        ge=1,
        le=1440,
        description="Время приготовления в минутах (от 1 до 1440 минут / 24 часов)",
        examples=[30],
    )
    difficulty: int = Field(
        ...,
        ge=1,
        le=5,
        description="Сложность приготовления: от 1 (очень легко) до 5 (шеф-повар)",
        examples=[2],
    )
    category: CategoryEnum = Field(
        ...,
        description="Категория приема пищи: breakfast, lunch, dinner, dessert, snack",
        examples=[CategoryEnum.breakfast],
    )


class RecipeCreate(RecipeBase):
    """Данные для создания нового рецепта."""

    pass


class RecipeUpdate(BaseModel):
    """Данные для частичного обновления рецепта (все поля опциональны)."""

    title: Optional[str] = Field(
        None,
        min_length=1,
        max_length=100,
        description="Новое название блюда",
        examples=["Блины тонкие заварные"],
    )
    description: Optional[str] = Field(
        None,
        min_length=1,
        max_length=500,
        description="Новое описание",
        examples=["Блины на кипятке и молоке с дырочками"],
    )
    cooking_time_minutes: Optional[int] = Field(
        None,
        ge=1,
        le=1440,
        description="Новое время приготовления в минутах",
        examples=[25],
    )
    difficulty: Optional[int] = Field(
        None,
        ge=1,
        le=5,
        description="Новая сложность (от 1 до 5)",
        examples=[3],
    )
    category: Optional[CategoryEnum] = Field(
        None,
        description="Новая категория блюда",
        examples=[CategoryEnum.breakfast],
    )


class RecipeResponse(RecipeBase):
    """Схема рецепта в ответе API."""

    id: int = Field(
        ...,
        description="Уникальный идентификатор рецепта в базе данных",
        examples=[1],
    )

    model_config = {"from_attributes": True}


class IngredientNested(BaseModel):
    """Ингредиент внутри подробной карточки рецепта."""

    id: int = Field(..., description="Уникальный ID ингредиента", examples=[1])
    name: str = Field(..., description="Название ингредиента", examples=["Мука пшеничная"])
    quantity: float = Field(..., description="Количество ингредиента", examples=[200.0])
    unit: str = Field(..., description="Единица измерения", examples=["g"])
    recipe_id: int = Field(..., description="ID связанного рецепта", examples=[1])

    model_config = {"from_attributes": True}


class RecipeDetailResponse(RecipeResponse):
    """Рецепт со списком связанных ингредиентов."""

    ingredients: List[IngredientNested] = Field(
        default_factory=list,
        description="Список всех ингредиентов, входящих в этот рецепт",
    )


# Обертки запросов/ответов по ТЗ для Recipe
class RecipeCreateRequest(BaseModel):
    """Тело входящего запроса на создание рецепта."""

    recipe: RecipeCreate

    model_config = {
        "json_schema_extra": {
            "example": {
                "recipe": {
                    "title": "Блины классические",
                    "description": "Тонкие аппетитные блины на молоке",
                    "cooking_time_minutes": 30,
                    "difficulty": 2,
                    "category": "breakfast",
                }
            }
        }
    }


class RecipeUpdateRequest(BaseModel):
    """Тело входящего запроса на частичное обновление рецепта."""

    recipe: RecipeUpdate

    model_config = {
        "json_schema_extra": {
            "example": {
                "recipe": {
                    "title": "Блины заварные",
                    "difficulty": 3,
                }
            }
        }
    }


class RecipeListResponse(BaseModel):
    """Список всех рецептов."""

    list: List[RecipeResponse] = Field(..., description="Массив найденных рецептов")


class RecipeSingleResponse(BaseModel):
    """Ответ с одним рецептом."""

    recipe: RecipeResponse


class RecipeDetailSingleResponse(BaseModel):
    """Ответ с одним рецептом и вложенными ингредиентами."""

    recipe: RecipeDetailResponse


# ---------------------------------------------------------------------------
# Ingredient Schemas
# ---------------------------------------------------------------------------


class IngredientBase(BaseModel):
    """Базовые поля ингредиента."""

    name: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Название ингредиента (до 100 символов)",
        examples=["Мука"],
    )
    quantity: float = Field(
        ...,
        gt=0,
        description="Количество (строго положительное число)",
        examples=[200.0],
    )
    unit: UnitEnum = Field(
        ...,
        description="Единица измерения (g, kg, ml, l, pcs, tbsp, tsp)",
        examples=[UnitEnum.g],
    )
    recipe_id: int = Field(
        ...,
        description="ID рецепта, к которому привязан ингредиент",
        examples=[1],
    )


class IngredientCreate(IngredientBase):
    """Данные для добавления нового ингредиента."""

    pass


class IngredientUpdate(BaseModel):
    """Данные для частичного обновления ингредиента (все поля опциональны)."""

    name: Optional[str] = Field(
        None,
        min_length=1,
        max_length=100,
        description="Новое название ингредиента",
        examples=["Мука пшеничная высший сорт"],
    )
    quantity: Optional[float] = Field(
        None,
        gt=0,
        description="Новое количество ингредиента",
        examples=[250.0],
    )
    unit: Optional[UnitEnum] = Field(
        None,
        description="Новая единица измерения",
        examples=[UnitEnum.g],
    )
    recipe_id: Optional[int] = Field(
        None,
        description="Перенос ингредиента в другой рецепт по ID",
        examples=[1],
    )


class IngredientResponse(IngredientBase):
    """Схема ингредиента в ответе API."""

    id: int = Field(
        ...,
        description="Уникальный идентификатор ингредиента",
        examples=[1],
    )

    model_config = {"from_attributes": True}


# Обертки запросов/ответов по ТЗ для Ingredient
class IngredientCreateRequest(BaseModel):
    """Тело входящего запроса на создание ингредиента."""

    ingredient: IngredientCreate

    model_config = {
        "json_schema_extra": {
            "example": {
                "ingredient": {
                    "name": "Мука пшеничная",
                    "quantity": 200.0,
                    "unit": "g",
                    "recipe_id": 1,
                }
            }
        }
    }


class IngredientUpdateRequest(BaseModel):
    """Тело входящего запроса на обновление ингредиента."""

    ingredient: IngredientUpdate

    model_config = {
        "json_schema_extra": {
            "example": {
                "ingredient": {
                    "quantity": 250.0,
                    "unit": "g",
                }
            }
        }
    }


class IngredientListResponse(BaseModel):
    """Список ингредиентов."""

    list: List[IngredientResponse] = Field(..., description="Массив найденных ингредиентов")


class IngredientSingleResponse(BaseModel):
    """Ответ с одним ингредиентом."""

    ingredient: IngredientResponse


# ---------------------------------------------------------------------------
# Error Schema
# ---------------------------------------------------------------------------


class ErrorResponse(BaseModel):
    """Стандартизированный формат ошибки по ТЗ."""

    status: int = Field(
        ...,
        description="HTTP статус-код ошибки (400, 404, 500)",
        examples=[400],
    )
    reason: str = Field(
        ...,
        description="Текстовое описание причины ошибки",
        examples=["Field 'title' is required"],
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "status": 400,
                "reason": "Field 'title': Field required",
            }
        }
    }
