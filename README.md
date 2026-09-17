# Recipe API — Сервис управления рецептами

RESTful API для управления кулинарными рецептами и их ингредиентами.

**Стек:** FastAPI + SQLAlchemy + Alembic + pytest

**БД:** SQLite по умолчанию (для простоты), PostgreSQL — через переменную окружения `DATABASE_URL`.

---

## Быстрый старт

### 1. Установить зависимости

```bash
cd recipe_api
pip install -r requirements.txt
```

### 2. Запустить сервер

```bash
uvicorn app.main:app --reload
```

Сервер доступен на http://localhost:8000

Документация Swagger UI: http://localhost:8000/docs

### 3. (Опционально) Использовать PostgreSQL

```bash
# Запустить PostgreSQL через Docker
docker-compose up -d

# Указать URL подключения
export DATABASE_URL="postgresql://postgres:postgres@localhost:5432/recipe_db"
uvicorn app.main:app --reload
```

---

## Модели

### Recipe (Рецепт)

| Поле | Тип | Ограничения |
|------|-----|-------------|
| id | int | PK |
| title | string | обязательное, до 100 символов |
| description | string | обязательное, до 500 символов |
| cooking_time_minutes | int | обязательное, 1–1440 |
| difficulty | int | обязательное, 1–5 |
| category | string | обязательное, одно из: breakfast / lunch / dinner / dessert / snack |

### Ingredient (Ингредиент)

| Поле | Тип | Ограничения |
|------|-----|-------------|
| id | int | PK |
| name | string | обязательное, до 100 символов |
| quantity | float | обязательное, > 0 |
| unit | string | обязательное, одно из: g / kg / ml / l / pcs / tbsp / tsp |
| recipe_id | int | обязательное, FK → Recipe |

---

## API Эндпоинты

### Рецепты

| Метод | URL | Описание | Коды |
|-------|-----|----------|------|
| GET | `/api/recipes` | Список всех рецептов | 200 |
| GET | `/api/recipes/{id}` | Рецепт по id (с ингредиентами) | 200, 404 |
| POST | `/api/recipes` | Создать рецепт | 200, 400, 500 |
| PATCH | `/api/recipes/{id}` | Обновить рецепт | 200, 400, 404, 500 |
| DELETE | `/api/recipes/{id}` | Удалить рецепт (каскадно) | 202, 404, 500 |

### Ингредиенты

| Метод | URL | Описание | Коды |
|-------|-----|----------|------|
| GET | `/api/ingredients` | Список всех ингредиентов | 200 |
| GET | `/api/ingredients/{id}` | Ингредиент по id | 200, 404 |
| POST | `/api/ingredients` | Создать ингредиент | 200, 400, 500 |
| PATCH | `/api/ingredients/{id}` | Обновить ингредиент | 200, 400, 404, 500 |
| DELETE | `/api/ingredients/{id}` | Удалить ингредиент | 202, 404, 500 |

---

## Примеры запросов

### Создать рецепт

```bash
curl -X POST http://localhost:8000/api/recipes \
  -H "Content-Type: application/json" \
  -d '{
    "recipe": {
      "title": "Блины",
      "description": "Классические тонкие блины на молоке",
      "cooking_time_minutes": 30,
      "difficulty": 2,
      "category": "breakfast"
    }
  }'
```

**Ответ (200):**
```json
{
  "recipe": {
    "id": 1,
    "title": "Блины",
    "description": "Классические тонкие блины на молоке",
    "cooking_time_minutes": 30,
    "difficulty": 2,
    "category": "breakfast"
  }
}
```

### Добавить ингредиент

```bash
curl -X POST http://localhost:8000/api/ingredients \
  -H "Content-Type: application/json" \
  -d '{
    "ingredient": {
      "name": "Мука",
      "quantity": 200,
      "unit": "g",
      "recipe_id": 1
    }
  }'
```

### Получить рецепт с ингредиентами

```bash
curl http://localhost:8000/api/recipes/1
```

**Ответ (200):**
```json
{
  "recipe": {
    "id": 1,
    "title": "Блины",
    "description": "Классические тонкие блины на молоке",
    "cooking_time_minutes": 30,
    "difficulty": 2,
    "category": "breakfast",
    "ingredients": [
      {
        "id": 1,
        "name": "Мука",
        "quantity": 200.0,
        "unit": "g",
        "recipe_id": 1
      }
    ]
  }
}
```

### Обновить рецепт (PATCH)

```bash
curl -X PATCH http://localhost:8000/api/recipes/1 \
  -H "Content-Type: application/json" \
  -d '{"recipe": {"difficulty": 4}}'
```

### Удалить рецепт

```bash
curl -X DELETE http://localhost:8000/api/recipes/1
# Ответ: 202 Accepted (ингредиенты удаляются каскадно)
```

### Ошибка валидации (400)

```json
{
  "status": 400,
  "reason": "Field 'title': Field required"
}
```

### Ошибка сервера (500)

```json
{
  "status": 500,
  "reason": "Database connection error"
}
```

---

## Тесты

```bash
python -m pytest tests/ -v
```

**38 тестов** покрывают:
- CRUD для рецептов и ингредиентов
- Валидацию полей (обязательность, диапазоны, enum-значения)
- Обработку пустого тела и невалидного JSON (HTTP 400)
- Ошибки 400/404/500 по формату ТЗ
- Каскадное удаление ингредиентов при удалении рецепта
- Проверку FK (нельзя создать ингредиент для несуществующего рецепта)

---

## Структура проекта

```
recipe_api/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI приложение, lifespan, exception handlers
│   ├── config.py            # Настройки, DATABASE_URL
│   ├── database.py          # SQLAlchemy engine, session, FK pragmas
│   ├── models.py            # Модели Recipe, Ingredient
│   ├── schemas.py           # Pydantic-схемы валидации и Swagger-модели
│   └── routers/
│       ├── __init__.py
│       ├── recipes.py       # CRUD для рецептов
│       └── ingredients.py   # CRUD для ингредиентов
├── tests/
│   ├── __init__.py
│   ├── conftest.py          # Фикстуры (изолированная тестовая БД, клиент)
│   ├── test_recipes.py      # 21 тест для рецептов
│   └── test_ingredients.py  # 17 тестов для ингредиентов
├── alembic/
│   ├── env.py
│   ├── script.py.mako
│   └── versions/
├── alembic.ini
├── Dockerfile               # Multi-stage сборка без root-прав
├── docker-compose.yml       # Сервисы app и db (PostgreSQL)
├── init.sql                 # Инициализация тестовой БД в Postgres
├── pyproject.toml           # Настройки линтера Ruff и Pytest
├── requirements.txt
└── README.md
```
