import os
import json
import base64
import pymysql
import pyotp
import qrcode

QR_DIR = "/home/app/qrcodes"
os.makedirs(QR_DIR, exist_ok=True)

def handle(req):
    """
    Generates a 2FA secret and QR code for a specified user, then updates the user's
    record in the database with the encoded secret.

    This function is designed to be used as a serverless OpenFaaS function. It uses 
    `pyotp` to generate a TOTP secret and `qrcode` to produce a scannable QR code 
    compatible with authenticator apps (like Google Authenticator or Authy).

    Parameters
    ----------
    req : str
        A JSON-formatted string containing the `username`.

    Returns
    -------
    str
        A JSON-formatted string with:
        - `username`: the target username
        - `raw_2fa_secret`: the generated TOTP secret in plain text
        - `encoded_secret`: base64-encoded version of the secret (for secure storage)
        - `qr_code_path`: path where the QR code image is saved
        - `status`: status message ("ok" or "error")

    Raises
    ------
    Returns an error message in JSON format if:
        - The `username` is missing
        - Database update fails
        - QR code generation fails
    """
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


# if __name__ == "__main__":
#     os.makedirs(QR_DIR, exist_ok=True)