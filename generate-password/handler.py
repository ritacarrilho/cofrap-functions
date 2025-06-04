import os
import json
import random
import string
import base64
import pymysql
import qrcode


QR_DIR = "/var/openfaas/qrcodes"
# os.makedirs(QR_DIR, exist_ok=True)

def generate_strong_password(length=24):
    """
    Generates a strong, complex password.

    The password includes uppercase and lowercase letters, digits, and special characters,
    randomly selected using `SystemRandom` for cryptographic security.

    Parameters
    ----------
    length : int, optional
        The desired length of the password (default is 24 characters).

    Returns
    -------
    str
        A randomly generated strong password string.
    """
    chars = string.ascii_letters + string.digits + string.punctuation
    return ''.join(random.SystemRandom().choice(chars) for _ in range(length))


def handle(req):
    """
    Generates a secure password for a given username, encodes it, saves it as a QR code,
    and stores it in the MariaDB database.

    If the user already exists, it updates the password and timestamp while keeping MFA untouched.
    A QR code is generated from the raw password and saved locally for display.

    Parameters
    ----------
    req : str
        A JSON-formatted string containing a `username` key.

    Returns
    -------
    str
        A JSON-formatted response containing:
        - `username`: the username provided
        - `raw_password`: the unencoded password (plaintext)
        - `encoded_password`: base64-encoded password for DB storage
        - `qr_code_path`: local file path where the QR code was saved
        - `status`: "ok" or error

    Raises
    ------
    Returns a JSON error message if:
        - Username is not provided
        - DB connection fails
        - QR code generation or file write fails
    """
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


if __name__ == "__main__":
    os.makedirs(QR_DIR, exist_ok=True)