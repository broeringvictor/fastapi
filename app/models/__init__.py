from sqlalchemy.orm import registry

# Registry/metadata central para toda a camada de models.
# Todos os modelos ORM devem usar este mesmo registry.
# Facilita a criação de testes unitários com bancos em memória.
table_registry = registry()


# Ao adicionar novos models, inclua-os aqui para adicionar aos metadados.
from . import user as user  # noqa: E402
