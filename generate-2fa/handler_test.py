from handler import handle
import json

def test_handle():
    request = json.dumps({"username": "john.doe"})
    response = handle(request)
    data = json.loads(response)

    assert data["status"] == "ok"
    assert "raw_2fa_secret" in data
    assert "encoded_secret" in data
    assert data["qr_code_path"].endswith(".png")