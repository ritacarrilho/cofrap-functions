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
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type"
    response.headers["Access-Control-Max-Age"] = "3600"
    return response


def handle(req):
    if request.method == "OPTIONS":
        response = make_response('', 204)  # No Content
        return add_cors_headers(response)

    try:
        data = json.loads(req)
        username = data.get("username")
        if not username:
            return add_cors_headers(make_response(json.dumps({"error": "username is required"}), 400))

        password = generate_strong_password()
        encoded_password = base64.b64encode(password.encode()).decode()

        # Generate QR code and save it
        img = qrcode.make(password)
        qr_path = f"{QR_DIR}/{username}_2fa_qr.png"
        img.save(qr_path)

        # Encode QR code as base64
        buffered = io.BytesIO()
        img.save(buffered, format="PNG")
        qr_code_base64 = base64.b64encode(buffered.getvalue()).decode()

        # Save password to DB
        connection = pymysql.connect(
            host=os.environ['DB_HOST'],
            user=os.environ['DB_USER'],
            password=os.environ['DB_PASSWORD'],
            database=os.environ['DB_NAME']
        )

        with connection:
            with connection.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO users (username, password, mfa, gendate, expired)
                    VALUES (%s, %s, '', UNIX_TIMESTAMP(), 0)
                    ON DUPLICATE KEY UPDATE password=%s, gendate=UNIX_TIMESTAMP(), expired=0
                """, (username, encoded_password, encoded_password))
            connection.commit()

        payload = {
            "username": username,
            "qr_code_base64": qr_code_base64,
            "status": "ok"
        }

        response = make_response(json.dumps(payload), 200)
        return add_cors_headers(response)

    except Exception as e:
        return add_cors_headers(make_response(json.dumps({"error": str(e)}), 500))