"""
Integration tests for the Module 12 calculation BREAD endpoints.

Named test_calculations_api.py to avoid clashing with the existing
Module 11 test_calculation_integration.py (factory/DB-level tests).
"""

import uuid

DUMMY_USER_ID = "3fa85f64-5717-4562-b3fc-2c963f66afa6"


def _create_calc(client, headers, type_="Add", a=2, b=3):
    return client.post(
        "/calculations",
        json={"type": type_, "a": a, "b": b, "user_id": DUMMY_USER_ID},
        headers=headers,
    )


# ---------------------------------------------------------------- Add
def test_add_calculation(client, auth_headers):
    resp = _create_calc(client, auth_headers, "Add", 2, 3)
    assert resp.status_code == 201
    data = resp.json()
    assert data["type"] == "Add"
    assert data["a"] == 2
    assert data["b"] == 3
    assert data["result"] == 5
    assert isinstance(data["id"], int)


def test_add_ignores_body_user_id(client, auth_headers):
    """Ownership must come from the token, not the request body."""
    resp = _create_calc(client, auth_headers, "Add", 1, 1)
    assert resp.status_code == 201
    assert resp.json()["user_id"] != DUMMY_USER_ID


def test_add_division_calculation(client, auth_headers):
    resp = _create_calc(client, auth_headers, "Divide", 100, 4)
    assert resp.status_code == 201
    assert resp.json()["result"] == 25


def test_add_divide_by_zero_fails(client, auth_headers):
    resp = _create_calc(client, auth_headers, "Divide", 10, 0)
    assert resp.status_code == 422


def test_add_invalid_type_fails(client, auth_headers):
    resp = _create_calc(client, auth_headers, "Modulus", 4, 2)
    assert resp.status_code == 422


def test_add_missing_operand_fails(client, auth_headers):
    resp = client.post(
        "/calculations",
        json={"type": "Add", "a": 5, "user_id": DUMMY_USER_ID},
        headers=auth_headers,
    )
    assert resp.status_code == 422


def test_add_requires_auth(client):
    resp = client.post(
        "/calculations",
        json={"type": "Add", "a": 1, "b": 2, "user_id": DUMMY_USER_ID},
    )
    assert resp.status_code == 401


# ---------------------------------------------------------------- Browse
def test_browse_calculations(client, auth_headers):
    _create_calc(client, auth_headers, "Add", 1, 2)
    _create_calc(client, auth_headers, "Multiply", 3, 4)

    resp = client.get("/calculations", headers=auth_headers)
    assert resp.status_code == 200
    assert len(resp.json()) == 2


def test_browse_only_shows_own_calculations(client, auth_headers):
    _create_calc(client, auth_headers, "Add", 1, 2)

    client.post(
        "/users/register",
        json={
            "username": "otheruser",
            "email": "other@example.com",
            "password": "Password123",
        },
    )
    login = client.post(
        "/users/login",
        json={"username": "otheruser", "password": "Password123"},
    )
    other_headers = {"Authorization": f"Bearer {login.json()['access_token']}"}

    resp = client.get("/calculations", headers=other_headers)
    assert resp.status_code == 200
    assert resp.json() == []


# ---------------------------------------------------------------- Read
def test_read_calculation(client, auth_headers):
    calc_id = _create_calc(client, auth_headers, "Sub", 10, 4).json()["id"]

    resp = client.get(f"/calculations/{calc_id}", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["id"] == calc_id
    assert data["result"] == 6


def test_read_nonexistent_calculation_404(client, auth_headers):
    resp = client.get("/calculations/999999", headers=auth_headers)
    assert resp.status_code == 404


def test_read_invalid_id_422(client, auth_headers):
    resp = client.get("/calculations/not-an-int", headers=auth_headers)
    assert resp.status_code == 422


# ---------------------------------------------------------------- Edit
def test_update_calculation_changes_type_and_recomputes(client, auth_headers):
    calc_id = _create_calc(client, auth_headers, "Add", 1, 1).json()["id"]

    resp = client.put(
        f"/calculations/{calc_id}",
        json={"type": "Multiply", "a": 6, "b": 7},
        headers=auth_headers,
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["type"] == "Multiply"
    assert data["result"] == 42


def test_update_operands_only(client, auth_headers):
    calc_id = _create_calc(client, auth_headers, "Add", 1, 1).json()["id"]

    resp = client.put(
        f"/calculations/{calc_id}",
        json={"a": 10, "b": 20},
        headers=auth_headers,
    )
    assert resp.status_code == 200
    assert resp.json()["result"] == 30


def test_update_to_divide_by_zero_fails(client, auth_headers):
    calc_id = _create_calc(client, auth_headers, "Divide", 10, 2).json()["id"]

    resp = client.put(
        f"/calculations/{calc_id}",
        json={"b": 0},
        headers=auth_headers,
    )
    assert resp.status_code == 422


def test_update_nonexistent_404(client, auth_headers):
    resp = client.put(
        "/calculations/999999",
        json={"a": 1, "b": 2},
        headers=auth_headers,
    )
    assert resp.status_code == 404


# ---------------------------------------------------------------- Delete
def test_delete_calculation(client, auth_headers):
    calc_id = _create_calc(client, auth_headers).json()["id"]

    resp = client.delete(f"/calculations/{calc_id}", headers=auth_headers)
    assert resp.status_code == 204

    resp = client.get(f"/calculations/{calc_id}", headers=auth_headers)
    assert resp.status_code == 404


def test_delete_nonexistent_404(client, auth_headers):
    resp = client.delete("/calculations/999999", headers=auth_headers)
    assert resp.status_code == 404
