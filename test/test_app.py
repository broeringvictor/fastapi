from fastapi.testclient import TestClient
from main import app

client = TestClient(app)




def test_root_should_return_hello_world():
    response = client.get("/")
    assert response.status_code == 200



