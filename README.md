# FastAPI Backend - Estudo e Template
Este projeto é um estudo e um modelo reutilizável de backend utilizando **FastAPI**.

O objetivo principal consiste em compreender as arquiteturas comumente adotadas no ecossistema Python, analisando especificamente as práticas de *Clean Code* e o nível de abstração utilizado na linguagem. O desenvolvimento foi orientado pela leitura de documentações e pela comparação direta com tecnologias do ecossistema .NET, visando entender:

* **Assincronismo:** Python `async/await` vs. C#.
* **ORM:** SQLAlchemy vs. Entity Framework.

## Funcionalidades e Arquitetura

O projeto segue uma arquitetura modular, com foco na separação de responsabilidades para facilitar manutenção e testes.

* **FastAPI**: Framework web principal.
* **Autenticação JWT**:
* Implementação de *Access Token* e *Refresh Token*.
* Armazenamento em **Cookies (HttpOnly)**.
* Proteção contra CSRF via configurações `SameSite` e `Secure`.




* **SQLAlchemy (Async)**: Estudo sobre a infraestrutura de banco de dados, incluindo a análise da necessidade de drivers síncronos para a execução de migrações.
* **Value Objects (VOs)**: Implementação de objetos de valor no domínio, adaptando o conceito frente à ausência de *structs* nativas no Python.
* **Testes Automatizados**:
* **Pytest & Pytest-Asyncio**: Testes unitários e de integração.
* **Factory Boy**: Geração de dados para testes.
* **Freezegun**: Manipulação temporal para validação de cenários (ex: expiração de tokens).


* **Gerenciamento de Dependências**: Utilização do `uv` para performance e padronização.

### Configuração (.env)

Crie um arquivo `.env` na raiz do projeto:

```dotenv
POSTGRES_USER=postgres
POSTGRES_PASSWORD=mysecretpassword
POSTGRES_DB=postgres
POSTGRES_PORT=5432
POSTGRES_HOST=localhost
SECRET_KEY=sua_chave_secreta_super_segura
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
AUTH_COOKIE_SECURE=True
AUTH_COOKIE_SAMESITE=lax

```

### Execução de Testes

Para execução da suíte de testes:

```bash
uv run task test

```

### Execução da Aplicação

Para iniciar o servidor em modo de desenvolvimento:

```bash
uv run fastapi dev main.py

```