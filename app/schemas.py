from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field

# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------


class CategoryEnum(str, Enum):
    breakfast = "breakfast"
    lunch = "lunch"
    dinner = "dinner"
    dessert = "dessert"
    snack = "snack"


class UnitEnum(str, Enum):
    g = "g"
    kg = "kg"
    ml = "ml"
    l = "l"
    pcs = "pcs"
    tbsp = "tbsp"
    tsp = "tsp"


# ---------------------------------------------------------------------------
# Recipe schemas
# ---------------------------------------------------------------------------


class RecipeCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=100)
    description: str = Field(..., min_length=1, max_length=500)
    cooking_time_minutes: int = Field(..., ge=1, le=1440)
    difficulty: int = Field(..., ge=1, le=5)
    category: CategoryEnum


class RecipeUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, min_length=1, max_length=500)
    cooking_time_minutes: Optional[int] = Field(None, ge=1, le=1440)
    difficulty: Optional[int] = Field(None, ge=1, le=5)
    category: Optional[CategoryEnum] = None


class RecipeResponse(BaseModel):
    id: int
    title: str
    description: str
    cooking_time_minutes: int
    difficulty: int
    category: str

    model_config = {"from_attributes": True}


class IngredientNested(BaseModel):
    """Ingredient as shown inside a recipe detail response."""

    id: int
    name: str
    quantity: float
    unit: str
    recipe_id: int

    model_config = {"from_attributes": True}


class RecipeDetailResponse(RecipeResponse):
    """Recipe with its nested list of ingredients."""

    ingredients: list[IngredientNested] = []


class RecipeCreateRequest(BaseModel):
    recipe: RecipeCreate


class RecipeUpdateRequest(BaseModel):
    recipe: RecipeUpdate


class RecipeListResponse(BaseModel):
    list: list[RecipeResponse]


class RecipeSingleResponse(BaseModel):
    recipe: RecipeResponse


class RecipeDetailSingleResponse(BaseModel):
    recipe: RecipeDetailResponse


# ---------------------------------------------------------------------------
# Ingredient schemas
# ---------------------------------------------------------------------------


class IngredientCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    quantity: float = Field(..., gt=0)
    unit: UnitEnum
    recipe_id: int


class IngredientUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    quantity: Optional[float] = Field(None, gt=0)
    unit: Optional[UnitEnum] = None
    recipe_id: Optional[int] = None


class IngredientResponse(BaseModel):
    id: int
    name: str
    quantity: float
    unit: str
    recipe_id: int

    model_config = {"from_attributes": True}


class IngredientCreateRequest(BaseModel):
    ingredient: IngredientCreate


class IngredientUpdateRequest(BaseModel):
    ingredient: IngredientUpdate


class IngredientListResponse(BaseModel):
    list: list[IngredientResponse]


class IngredientSingleResponse(BaseModel):
    ingredient: IngredientResponse


# ---------------------------------------------------------------------------
# Generic error schema for OpenAPI
# ---------------------------------------------------------------------------


class ErrorResponse(BaseModel):
    status: int
    reason: str
