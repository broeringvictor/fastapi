import pytest
from pydantic import ValidationError
from app.value_objects.email_vo import Email


def test_email_valid_creation():
    email = Email("Test@Example.com")
    # Verifica normalização para lowercase
    assert email.root == "test@example.com"
    assert str(email) == "test@example.com"


def test_email_invalid_cases():
    invalid_emails = [
        "plainaddress",
        "@missingusername.com",
        "username@.com",
        "username@com",
        "username@domain..com",
        "   ",  # Empty after strip
    ]

    for invalid_email in invalid_emails:
        with pytest.raises(ValidationError) as excinfo:
            Email(invalid_email)

        errors = excinfo.value.errors()
        # Verifica se a mensagem de erro personalizada está presente
        assert any("Email" in err["msg"] for err in errors)
