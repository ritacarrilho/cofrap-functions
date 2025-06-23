from handler import handle
import json
import base64
import pyotp

def test_handle():
    password = "le_mot_de_passe_en_clair"
    secret = "base64-secret-string"

    raw_secret = base64.b64decode(secret).decode()
    otp = pyotp.TOTP(raw_secret).now()

    request = json.dumps({
        "username": "john.doe",
        "password": password,
        "2fa_code": otp
    })
    response = handle(request)
    data = json.loads(response)

    assert data["status"] == "success"