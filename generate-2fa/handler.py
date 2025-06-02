import os
import json
import base64
import pymysql
import pyotp
import qrcode

QR_DIR = "/var/openfaas/qrcodes"
os.makedirs(QR_DIR, exist_ok=True)

def handle(req):
    try:
        data = json.loads(req)
        username = data.get("username")
        if not username:
            return json.dumps({"error": "username is required"})

        secret = pyotp.random_base32()

        totp = pyotp.TOTP(secret)
        uri = totp.provisioning_uri(name=username, issuer_name="Cofrap")
        
        img = qrcode.make(uri)
        qr_path = f"{QR_DIR}/{username}_pwd_qr.png"
        img.save(qr_path)

        encoded_secret = base64.b64encode(secret.encode()).decode()

        connection = pymysql.connect(
            host=os.environ['DB_HOST'],
            user=os.environ['DB_USER'],
            password=os.environ['DB_PASSWORD'],
            database=os.environ['DB_NAME']
        )

        with connection:
            with connection.cursor() as cursor:
                cursor.execute("""
                    UPDATE users
                    SET mfa = %s
                    WHERE username = %s
                """, (encoded_secret, username))
            connection.commit()

        return json.dumps({
            "username": username,
            "raw_2fa_secret": secret,
            "encoded_secret": encoded_secret,
            "qr_code_path": qr_path,
            "status": "ok"
        })

    except Exception as e:
        return json.dumps({ "error": str(e) })
