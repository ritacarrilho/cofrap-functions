import os
import io
import json
import base64
import pyotp
import pymysql
import qrcode
from flask import make_response

QR_DIR = "/home/app/qrcodes"
os.makedirs(QR_DIR, exist_ok=True)

def add_cors_headers(response):
    response.headers["Access-Control-Allow-Origin"]  = "*"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type"
    response.headers["Access-Control-Max-Age"]       = "3600"
    return response

def handle(req):
    """
    Generate a TOTP-based MFA secret for a user, encode it as a QR code,
    store the Base64-encoded secret in the database, and return the QR code as base64.

    This function handles CORS preflight requests and JSON POST requests with a `username`.

    Parameters
    ----------
    req : str
        A JSON-formatted string with the field:
        - `username` (str): the username for whom the MFA secret is generated.

    Returns
    -------
    JSON response
        If successful:
        {
            "code_mfa": "<base64-encoded QR code PNG>",
            "status": "ok"
        }

        If error:
        {
            "status": "error",
            "message": "<error details>"
        }

    Notes
    -----
    - The TOTP secret is generated using `pyotp.random_base32()`
    - The Base64-encoded secret is saved in the `mfa` field of the `users` table
    - The QR code is saved locally as a PNG file at `QR_DIR/<username>_2fa.png`
    - The QR code can be scanned by authenticator apps like Google Authenticator
    """
    if os.environ.get("REQUEST_METHOD") == "OPTIONS":
        return add_cors_headers(make_response("", 204))

    try:
        payload  = json.loads(req)
        username = payload.get("username") or ""
        if not username:
            resp = make_response(json.dumps({
                "status": "error",
                "message": "username is required"
            }), 400)
            return add_cors_headers(resp)

        secret   = pyotp.random_base32()
        totp     = pyotp.TOTP(secret, digits=6)
        code_2fa = totp.now()               

        uri = totp.provisioning_uri(name=username, issuer_name="Cofrap")
        img = qrcode.make(uri)
        qr_path = f"{QR_DIR}/{username}_2fa.png"
        img.save(qr_path)

        encoded_secret = base64.b64encode(secret.encode()).decode()
        buf            = io.BytesIO()
        img.save(buf, format="PNG")
        qr_b64         = base64.b64encode(buf.getvalue()).decode()

        conn = pymysql.connect(
            host     = os.environ['DB_HOST'],
            user     = os.environ['DB_USER'],
            password = os.environ['DB_PASSWORD'],
            database = os.environ['DB_NAME']
        )
        with conn:
            with conn.cursor() as cur:
                cur.execute("""
                    UPDATE users
                       SET mfa = %s
                     WHERE username = %s
                """, (encoded_secret, username))
            conn.commit()

        resp_body = {
            "code_mfa"    : qr_b64,
            "status"      : "ok"
        }
        resp = make_response(json.dumps(resp_body), 200)
        return add_cors_headers(resp)

    except Exception as e:
        resp = make_response(json.dumps({
            "status": "error",
            "message": str(e)
        }), 500)
        return add_cors_headers(resp)