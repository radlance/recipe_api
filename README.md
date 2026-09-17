# Recipe API — Сервис управления рецептами

[![CI/CD Pipeline](https://github.com/radlance/recipe_api/actions/workflows/ci.yml/badge.svg)](https://github.com/radlance/recipe_api/actions/workflows/ci.yml)

RESTful API сервис для управления кулинарными рецептами и их ингредиентами.

**Стек:** FastAPI + PostgreSQL (в Docker) / SQLite (локально) + SQLAlchemy + Alembic + Pytest

---

## 🚀 Быстрый старт через Docker

Для запуска сервиса и базы данных PostgreSQL требуется только установленный Docker. **Дополнительно настраивать файлы или переменные окружения не требуется.**

### 1. Запуск сервиса

```bash
docker compose up -d
```

Команда автоматически:
* Скачает образ PostgreSQL 16
* Соберёт образ приложения
* Дождётся готовности базы данных (`healthcheck`)
* Автоматически создаст необходимые таблицы в БД
* Запустит API на порту `8000`

### 2. Документация Swagger UI

После запуска откройте интерактивную документацию в браузере:
* **Swagger UI:** [http://localhost:8000/docs](http://localhost:8000/docs) (или [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs))
* **ReDoc:** [http://localhost:8000/redoc](http://localhost:8000/redoc)

В Swagger UI настроены примеры для кнопки **"Try it out"** — можно сразу тестировать любые запросы прямо из браузера.

### 3. Запуск тестов через Docker

Тесты запускаются одной командой внутри изолированного контейнера:

```bash
docker compose run --rm app pytest -v
```

Все **38 тестов** проверяют CRUD-операции, валидацию полей, каскадное удаление и форматы ошибок по ТЗ.

### 4. Остановка сервиса

```bash
docker compose down
```

---

## 💻 Альтернативный запуск: Локально (без Docker)

Если вы хотите запустить проект локально на SQLite:

```bash
# 1. Создать и активировать виртуальное окружение
python3 -m venv .venv
source .venv/bin/activate

# 2. Установить зависимости
pip install -r requirements.txt

# 3. Запустить тесты
pytest -v

# 4. Запустить локальный сервер
uvicorn app.main:app --reload
```

---

## 📋 Модели данных

### Recipe (Рецепт)

| Поле | Тип | Ограничения | Описание |
|------|-----|-------------|----------|
| `id` | int | Primary Key | Уникальный ID записи |
| `title` | string | 1–100 символов | Название рецепта |
| `description` | string | 1–500 символов | Описание приготовления |
| `cooking_time_minutes` | int | 1–1440 | Время готовки в минутах |
| `difficulty` | int | 1–5 | Сложность (от 1 до 5) |
| `category` | string | enum | `breakfast` / `lunch` / `dinner` / `dessert` / `snack` |

### Ingredient (Ингредиент)

| Поле | Тип | Ограничения | Описание |
|------|-----|-------------|----------|
| `id` | int | Primary Key | Уникальный ID записи |
| `name` | string | 1–100 символов | Название ингредиента |
| `quantity` | float | > 0 | Количество |
| `unit` | string | enum | `g` / `kg` / `ml` / `l` / `pcs` / `tbsp` / `tsp` |
| `recipe_id` | int | Foreign Key → Recipe | ID связанного рецепта (**ON DELETE CASCADE**) |

---

## 🔌 API Эндпоинты

### Рецепты (`/api/recipes`)

| Метод | URL | Описание | Коды ответов |
|---|---|---|---|
| `GET` | `/api/recipes` | Список всех рецептов | `200` |
| `GET` | `/api/recipes/{id}` | Рецепт по ID (с массивом ингредиентов) | `200`, `404` |
| `POST` | `/api/recipes` | Создать новый рецепт | `200`, `400`, `500` |
| `PATCH` | `/api/recipes/{id}` | Частично обновить поля рецепта | `200`, `400`, `404`, `500` |
| `DELETE` | `/api/recipes/{id}` | Удалить рецепт (каскадно удаляет ингредиенты) | `202`, `404`, `500` |

### Ингредиенты (`/api/ingredients`)

| Метод | URL | Описание | Коды ответов |
|---|---|---|---|
| `GET` | `/api/ingredients` | Список всех ингредиентов | `200` |
| `GET` | `/api/ingredients/{id}` | Ингредиент по ID | `200`, `404` |
| `POST` | `/api/ingredients` | Добавить ингредиент к рецепту | `200`, `400`, `500` |
| `PATCH` | `/api/ingredients/{id}` | Частично обновить поля ингредиента | `200`, `400`, `404`, `500` |
| `DELETE` | `/api/ingredients/{id}` | Удалить ингредиент по ID | `202`, `404`, `500` |

---

## 📌 Примеры запросов и ответов (по ТЗ)

### 1. Создание рецепта (POST)
```bash
curl -X POST http://localhost:8000/api/recipes \
  -H "Content-Type: application/json" \
  -d '{
    "recipe": {
      "title": "Блины классические",
      "description": "Тонкие аппетитные блины на молоке",
      "cooking_time_minutes": 30,
      "difficulty": 2,
      "category": "breakfast"
    }
  }'
```
**Ответ (200 OK):**
```json
{
  "recipe": {
    "id": 1,
    "title": "Блины классические",
    "description": "Тонкие аппетитные блины на молоке",
    "cooking_time_minutes": 30,
    "difficulty": 2,
    "category": "breakfast"
  }
}
```

### 2. Добавление ингредиента к рецепту (POST)
```bash
curl -X POST http://localhost:8000/api/ingredients \
  -H "Content-Type: application/json" \
  -d '{
    "ingredient": {
      "name": "Мука пшеничная",
      "quantity": 200.0,
      "unit": "g",
      "recipe_id": 1
    }
  }'
```

### 3. Получение рецепта со всеми ингредиентами (GET)
```bash
curl http://localhost:8000/api/recipes/1
```
**Ответ (200 OK):**
```json
{
  "recipe": {
    "id": 1,
    "title": "Блины классические",
    "description": "Тонкие аппетитные блины на молоке",
    "cooking_time_minutes": 30,
    "difficulty": 2,
    "category": "breakfast",
    "ingredients": [
      {
        "id": 1,
        "name": "Мука пшеничная",
        "quantity": 200.0,
        "unit": "g",
        "recipe_id": 1
      }
    ]
  }
}
```

### 4. Частичное обновление (PATCH)
```bash
curl -X PATCH http://localhost:8000/api/recipes/1 \
  -H "Content-Type: application/json" \
  -d '{"recipe": {"difficulty": 3}}'
```

### 5. Удаление (DELETE)
```bash
curl -X DELETE http://localhost:8000/api/recipes/1
```
**Ответ:** статус `202 Accepted` (связанные ингредиенты удаляются автоматически).

### 6. Ошибка валидации (400 Bad Request)
```json
{
  "status": 400,
  "reason": "Field 'title': Field required"
}
```

---

## 📂 Структура проекта

```
recipe_api/
├── app/
│   ├── __init__.py
│   ├── main.py              # Инициализация FastAPI, роутеры, обработчики ошибок
│   ├── config.py            # Настройки и URL базы данных
│   ├── database.py          # Сессия SQLAlchemy и engine
│   ├── models.py            # ORM модели Recipe и Ingredient (SQLAlchemy)
│   ├── schemas.py           # Pydantic-схемы валидации и Swagger-модели
│   └── routers/
│       ├── __init__.py
│       ├── recipes.py       # CRUD эндпоинты рецептов
│       └── ingredients.py   # CRUD эндпоинты ингредиентов
├── tests/
│   ├── __init__.py
│   ├── conftest.py          # Тестовая БД (SQLite в памяти) и TestClient
│   ├── test_recipes.py      # 21 тест для рецептов
│   └── test_ingredients.py  # 17 тестов для ингредиентов
├── alembic/
│   ├── env.py               # Конфигурация миграций
│   ├── script.py.mako
│   └── versions/
├── alembic.ini
├── Dockerfile               # Multi-stage сборка контейнера приложения
├── docker-compose.yml       # Сервисы приложения и БД (PostgreSQL 16)
├── init.sql                 # Инициализация тестовой базы в PostgreSQL
├── pyproject.toml           # Настройки линтера Ruff и тестов Pytest
├── requirements.txt
└── README.md
```
