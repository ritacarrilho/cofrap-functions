import os
import json
import random
import string
import base64
import pymysql
import qrcode
import io
from flask import request, make_response

# TODO: save user only once if it already exists

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