import os
import json
import pymysql
import base64
import pyotp
import time

# DB CONNECTION
def get_db_connection():
    return pymysql.connect(
        host=os.environ['DB_HOST'],
        user=os.environ['DB_USER'],
        password=os.environ['DB_PASSWORD'],
        database=os.environ['DB_NAME']
    )

# Decode base64-encoded values
def decode_b64(value):
    return base64.b64decode(value.encode()).decode()

# Check if the credentials are expired (> 6 months)
def is_expired(gendate_timestamp):
    now = int(time.time())
    six_months = 6 * 30 * 24 * 60 * 60
    return (now - int(gendate_timestamp)) > six_months

# 👤 Fetch user from DB
def fetch_user(username):
    connection = get_db_connection()
    with connection:
        with connection.cursor() as cursor:
            cursor.execute("SELECT password, mfa, gendate, expired FROM users WHERE username = %s", (username,))
            return cursor.fetchone()

# Mark user as expired
def mark_expired(username):
    connection = get_db_connection()
    with connection:
        with connection.cursor() as cursor:
            cursor.execute("UPDATE users SET expired = 1 WHERE username = %s", (username,))
        connection.commit()

# Auth logic
def authenticate_user(username, password, otp_code):
    user = fetch_user(username)
    if not user:
        return {"status": "auth_failed", "message": "User not found"}

    db_password_enc, mfa_enc, gendate, expired = user
    db_password = decode_b64(db_password_enc)
    mfa_secret = decode_b64(mfa_enc)

    # Check expiration
    if is_expired(gendate):
        mark_expired(username)
        return {"status": "expired", "message": "Password and MFA expired. Please reset credentials."}

    # Check password
    if db_password != password:
        return {"status": "auth_failed", "message": "Invalid password"}

    # Check TOTP
    totp = pyotp.TOTP(mfa_secret)
    if not totp.verify(otp_code, valid_window=1):
        return {"status": "auth_failed", "message": "Invalid 2FA code"}

    return {"status": "success", "message": "Authentication successful"}

def handle(req):
    try:
        data = json.loads(req)
        username = data.get("username")
        password = data.get("password")
        otp_code = data.get("2fa_code")

        if not username or not password or not otp_code:
            return json.dumps({"status": "error", "message": "Missing parameters"})

        result = authenticate_user(username, password, otp_code)
        return json.dumps(result)

    except Exception as e:
        return json.dumps({"status": "error", "message": str(e)})
