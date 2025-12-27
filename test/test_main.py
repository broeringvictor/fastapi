from http import HTTPStatus


# 1. Teste de Criação de Usuário
def test_create_user(client):
    response = client.post(
        "/users/",
        json={
            "name": "New User",
            "email": "newuser@example.com",
            "password": "S@@ecupord123",
        },
    )

    assert response.status_code == HTTPStatus.CREATED
    data = response.json()
    assert data["name"] == "New User"
    assert data["email"] == "newuser@example.com"
    # Garante que a senha não é retornada no modelo público
    assert "password" not in data


def test_create_user_email_already_exists(client, user_on_db):
    # Tenta criar um usuário com o mesmo e-mail do user_on_db (fixture)
    response = client.post(
        "/users/",
        json={
            "name": "Duplicate User",
            "email": user_on_db.email.root,  # Acessa a string do VO Email
            "password": "S@@ecupassword123",
        },
    )

    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert response.json()["detail"] == "Email already registered."


# 2. Teste de Leitura Pública (Busca por E-mail)
def test_get_user_by_email(client, user_on_db):
    # Dependendo de como GetByEmail está definido, pode ser query param
    response = client.get("/users/", params={"email": user_on_db.email.root})

    assert response.status_code == HTTPStatus.OK
    assert response.json()["name"] == user_on_db.name


# 3. Teste de Login e Segurança
def test_login_success(client, user_on_db):
    response = client.post(
        "/login",
        json={
            "email": user_on_db.email.root,
            "password": "S@@ecupassword12",  # Senha definida na fixture user_on_db
        },
    )

    assert response.status_code == HTTPStatus.OK
    # Verifica se o cookie foi definido na resposta
    assert "access_token" in response.cookies
    assert response.json()["email"] == user_on_db.email.root


def test_login_wrong_password(client, user_on_db):
    response = client.post(
        "/login",
        json={
            "email": user_on_db.email.root,
            "password": "WRONG_PASSWORD",
        },
    )

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert "access_token" not in response.cookies


# 4. Testes de Rotas Protegidas (PATCH, DELETE, ME)


def test_read_me(client, user_on_db):
    # 1. Faz login para obter o cookie
    client.post(
        "/login",
        json={"email": user_on_db.email.root, "password": "S@@ecupassword12"},
    )

    # 2. O TestClient mantém os cookies automaticamente para as próximas requisições
    response = client.get("/users/me")

    assert response.status_code == HTTPStatus.OK
    assert response.json()["email"] == user_on_db.email.root


def test_read_me_unauthorized(client):
    # Sem fazer login antes
    response = client.get("/users/me")
    assert response.status_code == HTTPStatus.UNAUTHORIZED


def test_patch_user(client, user_on_db):
    # 1. Login
    client.post(
        "/login",
        json={"email": user_on_db.email.root, "password": "S@@ecupassword12"},
    )

    # 2. Patch
    response = client.patch(
        "/users/",
        json={"name": "Updated Name", "new_email": "updated@example.com"},
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json()["name"] == "Updated Name"
    assert response.json()["email"] == "updated@example.com"


def test_delete_user(client, user_on_db):
    # 1. Login
    client.post(
        "/login",
        json={"email": user_on_db.email.root, "password": "S@@ecupassword12"},
    )

    # 2. Delete (com confirmação True)
    response = client.request(
        "DELETE",
        "/users/",
        json={"confirmation": True},
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json()["message"] == "User deleted successfully"

    # 3. Verifica se o cookie foi removido (o valor fica vazio ou expirado)
    # No TestClient, verificar se o cookie foi deletado pode variar,
    # mas tentar acessar /users/me deve falhar agora pois o user foi deletado do banco
    # OU porque o cookie foi invalidado.

    # Verifica banco de dados (via rota protegida, deve falhar no get_current_user)
    res_check = client.get("/users/me")
    # Como o usuário foi deletado do banco, get_current_user retorna 401
    assert res_check.status_code == HTTPStatus.UNAUTHORIZED


def test_logout(client, user_on_db):
    # 1. Login
    client.post(
        "/login",
        json={"email": user_on_db.email.root, "password": "S@@ecupassword12"},
    )

    # 2. Logout
    response = client.post("/logout")
    assert response.status_code == HTTPStatus.OK

    # 3. Tenta acessar rota protegida
    response_me = client.get("/users/me")
    assert response_me.status_code == HTTPStatus.UNAUTHORIZED
