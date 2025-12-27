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


@pytest.mark.asyncio
async def test_login_returns_refresh_token(client, user_on_db):
    response = client.post(
        "/auth/",
        json={
            "email": user_on_db.email.root,
            "password": "DefaultP@ssw0rd!",
        },
    )

    assert response.status_code == status.HTTP_200_OK
    assert "access_token" in response.cookies
    assert "refresh_token" in response.cookies


@pytest.mark.asyncio
async def test_refresh_token_success(client, user_on_db):
    # 1. Login para pegar o refresh token
    client.post(
        "/auth/",
        json={
            "email": user_on_db.email.root,
            "password": "DefaultP@ssw0rd!",
        },
    )

    # Limpa os cookies do client para simular expiração do access token
    # (embora o endpoint /refresh leia do cookie, vamos garantir que estamos enviando apenas o necessário se fosse manual,
    # mas o TestClient gerencia cookies automaticamente. Vamos forçar o envio do refresh token se precisarmos,
    # mas o comportamento padrão é enviar todos os cookies do domínio).

    # Vamos chamar o refresh. O client deve enviar os cookies recebidos no login.
    response = client.post("/auth/refresh")

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"message": "Access token refreshed"}

    # Verifica se um novo access token foi definido (ou o mesmo renovado)
    assert "access_token" in response.cookies


@pytest.mark.asyncio
async def test_refresh_token_missing(client):
    # Chama refresh sem ter logado (sem cookies)
    client.cookies.clear()  # Garante que não tem cookies
    response = client.post("/auth/refresh")

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json()["detail"] == "Refresh token missing"


@pytest.mark.asyncio
async def test_refresh_token_invalid(client):
    # Define um cookie inválido manualmente
    client.cookies.set("refresh_token", "invalid_token")

    response = client.post("/auth/refresh")

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json()["detail"] == "Invalid refresh token"
