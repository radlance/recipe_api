from tests.conftest import make_recipe_payload

# ---------------------------------------------------------------------------
# GET /api/recipes
# ---------------------------------------------------------------------------


class TestGetRecipes:
    def test_empty_list(self, client):
        resp = client.get("/api/recipes")
        assert resp.status_code == 200
        assert resp.json() == {"list": []}

    def test_list_after_creation(self, client):
        client.post("/api/recipes", json=make_recipe_payload())
        client.post(
            "/api/recipes",
            json=make_recipe_payload(title="Омлет", category="breakfast"),
        )
        resp = client.get("/api/recipes")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data["list"]) == 2


# ---------------------------------------------------------------------------
# GET /api/recipes/:id
# ---------------------------------------------------------------------------


class TestGetRecipeById:
    def test_existing(self, client):
        create_resp = client.post("/api/recipes", json=make_recipe_payload())
        recipe_id = create_resp.json()["recipe"]["id"]

        resp = client.get(f"/api/recipes/{recipe_id}")
        assert resp.status_code == 200
        recipe = resp.json()["recipe"]
        assert recipe["title"] == "Блины"
        assert "ingredients" in recipe

    def test_not_found(self, client):
        resp = client.get("/api/recipes/9999")
        assert resp.status_code == 404


# ---------------------------------------------------------------------------
# POST /api/recipes
# ---------------------------------------------------------------------------


class TestCreateRecipe:
    def test_success(self, client):
        resp = client.post("/api/recipes", json=make_recipe_payload())
        assert resp.status_code == 200
        recipe = resp.json()["recipe"]
        assert recipe["title"] == "Блины"
        assert recipe["difficulty"] == 2
        assert recipe["category"] == "breakfast"
        assert "id" in recipe

    def test_missing_title(self, client):
        payload = make_recipe_payload()
        del payload["recipe"]["title"]
        resp = client.post("/api/recipes", json=payload)
        assert resp.status_code == 400
        assert "title" in resp.json()["reason"]

    def test_invalid_difficulty_too_high(self, client):
        resp = client.post("/api/recipes", json=make_recipe_payload(difficulty=10))
        assert resp.status_code == 400
        assert "difficulty" in resp.json()["reason"]

    def test_invalid_difficulty_too_low(self, client):
        resp = client.post("/api/recipes", json=make_recipe_payload(difficulty=0))
        assert resp.status_code == 400

    def test_invalid_category(self, client):
        resp = client.post("/api/recipes", json=make_recipe_payload(category="invalid"))
        assert resp.status_code == 400

    def test_cooking_time_too_high(self, client):
        resp = client.post("/api/recipes", json=make_recipe_payload(cooking_time_minutes=9999))
        assert resp.status_code == 400

    def test_cooking_time_zero(self, client):
        resp = client.post("/api/recipes", json=make_recipe_payload(cooking_time_minutes=0))
        assert resp.status_code == 400

    def test_title_too_long(self, client):
        resp = client.post("/api/recipes", json=make_recipe_payload(title="A" * 101))
        assert resp.status_code == 400

    def test_missing_recipe_wrapper(self, client):
        resp = client.post(
            "/api/recipes",
            json={
                "title": "Блины",
                "description": "...",
                "cooking_time_minutes": 30,
                "difficulty": 2,
                "category": "breakfast",
            },
        )
        assert resp.status_code == 400
        assert "recipe" in resp.json()["reason"].lower()

    def test_empty_body(self, client):
        resp = client.post("/api/recipes", content=b"")
        assert resp.status_code == 400
        assert resp.json()["status"] == 400

    def test_malformed_json(self, client):
        resp = client.post(
            "/api/recipes",
            content=b"{invalid json",
            headers={"content-type": "application/json"},
        )
        assert resp.status_code == 400
        assert resp.json()["status"] == 400


# ---------------------------------------------------------------------------
# PATCH /api/recipes/:id
# ---------------------------------------------------------------------------


class TestUpdateRecipe:
    def test_partial_update(self, client):
        create_resp = client.post("/api/recipes", json=make_recipe_payload())
        recipe_id = create_resp.json()["recipe"]["id"]

        resp = client.patch(
            f"/api/recipes/{recipe_id}",
            json={"recipe": {"difficulty": 5, "title": "Блины тонкие"}},
        )
        assert resp.status_code == 200
        recipe = resp.json()["recipe"]
        assert recipe["difficulty"] == 5
        assert recipe["title"] == "Блины тонкие"
        # Unchanged fields should remain
        assert recipe["cooking_time_minutes"] == 30

    def test_not_found(self, client):
        resp = client.patch("/api/recipes/9999", json={"recipe": {"difficulty": 3}})
        assert resp.status_code == 404

    def test_invalid_field_value(self, client):
        create_resp = client.post("/api/recipes", json=make_recipe_payload())
        recipe_id = create_resp.json()["recipe"]["id"]

        resp = client.patch(
            f"/api/recipes/{recipe_id}",
            json={"recipe": {"difficulty": 99}},
        )
        assert resp.status_code == 400


# ---------------------------------------------------------------------------
# DELETE /api/recipes/:id
# ---------------------------------------------------------------------------


class TestDeleteRecipe:
    def test_success(self, client):
        create_resp = client.post("/api/recipes", json=make_recipe_payload())
        recipe_id = create_resp.json()["recipe"]["id"]

        resp = client.delete(f"/api/recipes/{recipe_id}")
        assert resp.status_code == 202

        # Verify it's actually gone
        resp = client.get(f"/api/recipes/{recipe_id}")
        assert resp.status_code == 404

    def test_not_found(self, client):
        resp = client.delete("/api/recipes/9999")
        assert resp.status_code == 404

    def test_cascade_deletes_ingredients(self, client):
        """Deleting a recipe must also delete its ingredients."""
        from tests.conftest import make_ingredient_payload

        create_resp = client.post("/api/recipes", json=make_recipe_payload())
        recipe_id = create_resp.json()["recipe"]["id"]

        # Add ingredients
        client.post(
            "/api/ingredients",
            json=make_ingredient_payload(recipe_id, name="Мука"),
        )
        client.post(
            "/api/ingredients",
            json=make_ingredient_payload(recipe_id, name="Молоко", unit="ml"),
        )

        # Delete recipe
        resp = client.delete(f"/api/recipes/{recipe_id}")
        assert resp.status_code == 202

        # Ingredients should be gone too
        resp = client.get("/api/ingredients")
        assert resp.status_code == 200
        assert resp.json()["list"] == []
