import os
import json
import random
import string
import base64
import pymysql
import qrcode
import io
from flask import request, make_response

QR_DIR = "/home/app/qrcodes"
os.makedirs(QR_DIR, exist_ok=True)

def generate_strong_password(length=24):
    chars = string.ascii_letters + string.digits + string.punctuation
    return ''.join(random.SystemRandom().choice(chars) for _ in range(length))

def add_cors_headers(response):
    response.headers["Access-Control-Allow-Origin"]  = "*"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type"
    response.headers["Access-Control-Max-Age"]       = "3600"
    return response

def handle(req):
    """
    Generate a strong password for a user, store it in the database (encoded),
    and return a QR code representing the password in base64 format.

    This function handles CORS preflight requests and JSON POST requests with a `username`.
    If the user already exists, their password is updated; otherwise, a new user is created.

    Parameters
    ----------
    req : str
        A JSON-formatted string with the field:
        - `username` (str): the username for which to generate or update a password.

    Returns
    -------
    JSON response
        If successful:
        {
            "status": "ok",
            "qr_code_base64": "<base64-encoded QR code PNG for the password>"
        }

        If error:
        {
            "status": "error",
            "message": "<error message>"
        }

    Notes
    -----
    - A strong password is randomly generated using letters, digits, and punctuation.
    - The password is encoded in Base64 and stored in the `password` field of the `users` table.
    - The QR code is saved to `QR_DIR/<username>_pwd_qr.png` and returned as a base64 string.
    - The function supports updating an existing user or creating a new one.
    """
    # Handle CORS preflight
    if request.method == "OPTIONS":
        return add_cors_headers(make_response('', 204))

    try:
        data     = json.loads(req)
        username = data.get("username") or ""
        if not username:
            return add_cors_headers(
                make_response(json.dumps({
                    "status": "error",
                    "message": "username is required"
                }), 400)
            )

        conn   = pymysql.connect(
            host     = os.environ['DB_HOST'],
            user     = os.environ['DB_USER'],
            password = os.environ['DB_PASSWORD'],
            database = os.environ['DB_NAME']
        )
        cursor = conn.cursor()

        cursor.execute("SELECT 1 FROM users WHERE username = %s", (username,))
        exists = cursor.fetchone() is not None

        raw_pass     = generate_strong_password()
        encoded_pass = base64.b64encode(raw_pass.encode()).decode()

        img      = qrcode.make(raw_pass)
        qr_path  = f"{QR_DIR}/{username}_pwd_qr.png"
        img.save(qr_path)

        if exists:
            cursor.execute("""
                UPDATE users
                   SET password = %s,
                       gendate  = UNIX_TIMESTAMP(),
                       expired  = 0
                 WHERE username = %s
            """, (encoded_pass, username))

        else:
            cursor.execute("""
                INSERT INTO users
                    (username, password, mfa, gendate, expired)
                VALUES
                    (%s, %s, '', UNIX_TIMESTAMP(), 0)
            """, (username, encoded_pass))

        conn.commit()
        cursor.close()
        conn.close()

        buf         = io.BytesIO()
        img.save(buf, format="PNG")
        qr_b64      = base64.b64encode(buf.getvalue()).decode()
        payload     = {
            "status"           : "ok",
            "qr_code_base64"   : qr_b64
        }
        resp = make_response(json.dumps(payload), 200)
        return add_cors_headers(resp)

    except Exception as e:
        return add_cors_headers(
            make_response(json.dumps({
                "status": "error",
                "message": str(e)
            }), 500)
        )