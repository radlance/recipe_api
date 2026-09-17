import os

# SQLite by default — easy local development; switch to PostgreSQL in production.
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "sqlite:///./recipe.db",
)

TEST_DATABASE_URL = os.getenv(
    "TEST_DATABASE_URL",
    "sqlite:///./test_recipe.db",
)
