import json
from handler import handle


def test_handle():
    request = json.dumps({"username": "john.doe"})
    response = handle(request)
    data = json.loads(response)

    assert data["status"] == "ok"
    assert "raw_password" in data
    assert "encoded_password" in data
    assert data["qr_code_path"].endswith(".png")