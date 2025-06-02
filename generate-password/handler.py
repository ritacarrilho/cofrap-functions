import os
import json
import random
import string
import base64
import pymysql
import qrcode

QR_DIR = "/var/openfaas/qrcodes"
os.makedirs(QR_DIR, exist_ok=True)

def generate_strong_password(length=24):
    chars = string.ascii_letters + string.digits + string.punctuation
    return ''.join(random.SystemRandom().choice(chars) for _ in range(length))

def handle(req):
    try:
        data = json.loads(req)
        username = data.get("username")
        if not username:
            return json.dumps({"error": "username is required"})

        password = generate_strong_password()
        encoded_password = base64.b64encode(password.encode()).decode()

        img = qrcode.make(password)
        qr_path = f"{QR_DIR}/{username}_2fa_qr.png"
        img.save(qr_path)

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

        return json.dumps({
            "username": username,
            "raw_password": password,
            "encoded_password": encoded_password,
            "qr_code_path": qr_path,
            "status": "ok"
        })

    except Exception as e:
        return json.dumps({"error": str(e)})
