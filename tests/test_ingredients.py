from tests.conftest import make_ingredient_payload, make_recipe_payload


def _create_recipe(client) -> int:
    """Helper: create a recipe and return its id."""
    resp = client.post("/api/recipes", json=make_recipe_payload())
    return resp.json()["recipe"]["id"]


# ---------------------------------------------------------------------------
# GET /api/ingredients
# ---------------------------------------------------------------------------


class TestGetIngredients:
    def test_empty_list(self, client):
        resp = client.get("/api/ingredients")
        assert resp.status_code == 200
        assert resp.json() == {"list": []}

    def test_list_after_creation(self, client):
        recipe_id = _create_recipe(client)
        client.post(
            "/api/ingredients",
            json=make_ingredient_payload(recipe_id, name="Мука"),
        )
        client.post(
            "/api/ingredients",
            json=make_ingredient_payload(recipe_id, name="Молоко", unit="ml"),
        )
        resp = client.get("/api/ingredients")
        assert resp.status_code == 200
        assert len(resp.json()["list"]) == 2


# ---------------------------------------------------------------------------
# GET /api/ingredients/:id
# ---------------------------------------------------------------------------


class TestGetIngredientById:
    def test_existing(self, client):
        recipe_id = _create_recipe(client)
        create_resp = client.post(
            "/api/ingredients",
            json=make_ingredient_payload(recipe_id),
        )
        ing_id = create_resp.json()["ingredient"]["id"]

        resp = client.get(f"/api/ingredients/{ing_id}")
        assert resp.status_code == 200
        ingredient = resp.json()["ingredient"]
        assert ingredient["name"] == "Мука"
        assert ingredient["recipe_id"] == recipe_id

    def test_not_found(self, client):
        resp = client.get("/api/ingredients/9999")
        assert resp.status_code == 404


# ---------------------------------------------------------------------------
# POST /api/ingredients
# ---------------------------------------------------------------------------


class TestCreateIngredient:
    def test_success(self, client):
        recipe_id = _create_recipe(client)
        resp = client.post(
            "/api/ingredients",
            json=make_ingredient_payload(recipe_id),
        )
        assert resp.status_code == 200
        ingredient = resp.json()["ingredient"]
        assert ingredient["name"] == "Мука"
        assert ingredient["quantity"] == 200.0
        assert ingredient["unit"] == "g"
        assert ingredient["recipe_id"] == recipe_id

    def test_missing_name(self, client):
        recipe_id = _create_recipe(client)
        payload = make_ingredient_payload(recipe_id)
        del payload["ingredient"]["name"]
        resp = client.post("/api/ingredients", json=payload)
        assert resp.status_code == 400
        assert "name" in resp.json()["reason"]

    def test_invalid_unit(self, client):
        recipe_id = _create_recipe(client)
        resp = client.post(
            "/api/ingredients",
            json=make_ingredient_payload(recipe_id, unit="invalid_unit"),
        )
        assert resp.status_code == 400

    def test_zero_quantity(self, client):
        recipe_id = _create_recipe(client)
        resp = client.post(
            "/api/ingredients",
            json=make_ingredient_payload(recipe_id, quantity=0),
        )
        assert resp.status_code == 400

    def test_negative_quantity(self, client):
        recipe_id = _create_recipe(client)
        resp = client.post(
            "/api/ingredients",
            json=make_ingredient_payload(recipe_id, quantity=-5),
        )
        assert resp.status_code == 400

    def test_nonexistent_recipe_id(self, client):
        resp = client.post(
            "/api/ingredients",
            json=make_ingredient_payload(recipe_id=9999),
        )
        assert resp.status_code == 400
        assert "9999" in resp.json()["reason"]

    def test_missing_ingredient_wrapper(self, client):
        recipe_id = _create_recipe(client)
        resp = client.post(
            "/api/ingredients",
            json={"name": "Мука", "quantity": 200, "unit": "g", "recipe_id": recipe_id},
        )
        assert resp.status_code == 400
        assert "ingredient" in resp.json()["reason"].lower()


# ---------------------------------------------------------------------------
# PATCH /api/ingredients/:id
# ---------------------------------------------------------------------------


class TestUpdateIngredient:
    def test_partial_update(self, client):
        recipe_id = _create_recipe(client)
        create_resp = client.post(
            "/api/ingredients",
            json=make_ingredient_payload(recipe_id),
        )
        ing_id = create_resp.json()["ingredient"]["id"]

        resp = client.patch(
            f"/api/ingredients/{ing_id}",
            json={"ingredient": {"name": "Мука пшеничная", "quantity": 300}},
        )
        assert resp.status_code == 200
        ingredient = resp.json()["ingredient"]
        assert ingredient["name"] == "Мука пшеничная"
        assert ingredient["quantity"] == 300.0
        # Unchanged fields
        assert ingredient["unit"] == "g"

    def test_not_found(self, client):
        resp = client.patch(
            "/api/ingredients/9999",
            json={"ingredient": {"name": "test"}},
        )
        assert resp.status_code == 404

    def test_update_to_nonexistent_recipe(self, client):
        recipe_id = _create_recipe(client)
        create_resp = client.post(
            "/api/ingredients",
            json=make_ingredient_payload(recipe_id),
        )
        ing_id = create_resp.json()["ingredient"]["id"]

        resp = client.patch(
            f"/api/ingredients/{ing_id}",
            json={"ingredient": {"recipe_id": 9999}},
        )
        assert resp.status_code == 400

    def test_invalid_quantity(self, client):
        recipe_id = _create_recipe(client)
        create_resp = client.post(
            "/api/ingredients",
            json=make_ingredient_payload(recipe_id),
        )
        ing_id = create_resp.json()["ingredient"]["id"]

        resp = client.patch(
            f"/api/ingredients/{ing_id}",
            json={"ingredient": {"quantity": -1}},
        )
        assert resp.status_code == 400


# ---------------------------------------------------------------------------
# DELETE /api/ingredients/:id
# ---------------------------------------------------------------------------


class TestDeleteIngredient:
    def test_success(self, client):
        recipe_id = _create_recipe(client)
        create_resp = client.post(
            "/api/ingredients",
            json=make_ingredient_payload(recipe_id),
        )
        ing_id = create_resp.json()["ingredient"]["id"]

        resp = client.delete(f"/api/ingredients/{ing_id}")
        assert resp.status_code == 202

        # Verify it's gone
        resp = client.get(f"/api/ingredients/{ing_id}")
        assert resp.status_code == 404

    def test_not_found(self, client):
        resp = client.delete("/api/ingredients/9999")
        assert resp.status_code == 404
