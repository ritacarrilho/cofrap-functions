import os
import json
import base64
import pyotp
import pymysql
import qrcode

QR_DIR = "/home/app/qrcodes"
os.makedirs(QR_DIR, exist_ok=True)

def handle(req):
    """
    Generates a TOTP secret and 6‑digit code for a specified user,
    stores the Base64‑encoded secret in the database, and returns
    the 6‑digit code in the response.

    req : str
        JSON string containing {"username": "<user>"}

    Returns
    -------
    str
        JSON-formatted:
        {
          "code_2fa": "123456",
          "status": "ok"
        }
    """
    try:
        payload = json.loads(req)
        username = payload.get("username")
        if not username:
            return json.dumps({"error": "username is required"}), 400

        secret = pyotp.random_base32()                  
        totp = pyotp.TOTP(secret, digits=6)             
        code_2fa = totp.now()                           

        uri = totp.provisioning_uri(name=username, issuer_name="Cofrap")
        qr_path = f"{QR_DIR}/{username}_2fa.png"
        img = qrcode.make(uri)
        img.save(qr_path)

        encoded_secret = base64.b64encode(secret.encode()).decode()

        conn = pymysql.connect(
            host=os.environ['DB_HOST'],
            user=os.environ['DB_USER'],
            password=os.environ['DB_PASSWORD'],
            database=os.environ['DB_NAME']
        )

        with conn:
            with conn.cursor() as cur:
                cur.execute("""
                    UPDATE users
                    SET mfa = %s
                    WHERE username = %s
                """, (encoded_secret, username))
            conn.commit()

        return json.dumps({
            "code_mfa": code_2fa,
            "status": "ok"
        })

    except Exception as e:
        return json.dumps({"error": str(e)}), 500