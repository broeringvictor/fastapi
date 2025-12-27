import pytest
from fastapi import status


@pytest.mark.asyncio
async def test_login_with_invalid_email(client):
    # Tenta logar com email inválido
    response = client.post(
        "/auth/", json={"email": "invalid-email", "password": "password123"}
    )

    # Deve retornar 422 Unprocessable Entity (validação do Pydantic)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

    data = response.json()
    # Verifica se o erro é sobre o email
    assert data["detail"][0]["loc"] == ["body", "email"]
    assert "Email inválido" in data["detail"][0]["msg"]


@pytest.mark.asyncio
async def test_login_with_valid_email_structure(client, user_on_db):
    # Tenta logar com email válido (estrutura), mas credenciais erradas
    # Isso garante que passou da validação do Pydantic e chegou na lógica de auth
    response = client.post(
        "/auth/",
        json={"email": "valid@email.com", "password": "wrongpassword"},
    )

    # Deve retornar 401 Unauthorized (lógica de negócio)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
