import os
import json
import pymysql
import base64
import pyotp
import time


def get_db_connection():
    """
    Establish a connection to the MariaDB database using credentials 
    and host information from environment variables.
    
    Returns
    -------
    pymysql.Connection
        An active connection object to the MariaDB database.
    """
    return pymysql.connect(
        host=os.environ['DB_HOST'],
        user=os.environ['DB_USER'],
        password=os.environ['DB_PASSWORD'],
        database=os.environ['DB_NAME']
    )


def decode_b64(value):
    """
    Decode a base64-encoded string.

    Parameters
    ----------
    value : str
        A base64-encoded string.

    Returns
    -------
    str
        The decoded plaintext string.
    """
    return base64.b64decode(value.encode()).decode()



def is_expired(gendate_timestamp):
    """
    Check whether the credentials are older than 6 months.

    Parameters
    ----------
    gendate_timestamp : int
        Timestamp indicating when the credentials were generated.

    Returns
    -------
    bool
        True if credentials are expired, False otherwise.
    """
    now = int(time.time())
    six_months = 6 * 30 * 24 * 60 * 60
    return (now - int(gendate_timestamp)) > six_months


def fetch_user(username):
    """
    Retrieve user details from the database.

    Parameters
    ----------
    username : str
        The username whose data needs to be fetched.

    Returns
    -------
    tuple or None
        A tuple containing (password, mfa, gendate, expired) or None if user is not found.
    """
    connection = get_db_connection()
    with connection:
        with connection.cursor() as cursor:
            cursor.execute("SELECT password, mfa, gendate, expired FROM users WHERE username = %s", (username,))
            return cursor.fetchone()


def mark_expired(username):
    """
    Update the user’s status to 'expired' in the database.

    Parameters
    ----------
    username : str
        The username to be marked as expired.
    """
    connection = get_db_connection()
    with connection:
        with connection.cursor() as cursor:
            cursor.execute("UPDATE users SET expired = 1 WHERE username = %s", (username,))
        connection.commit()


def authenticate_user(username, password, otp_code):
    """
    Authenticate a user by checking their password and TOTP 2FA code.

    Parameters
    ----------
    username : str
        The user’s login.
    password : str
        The raw password entered by the user.
    otp_code : str
        The 2FA code from the user's authenticator app.

    Returns
    -------
    dict
        A JSON-serializable dictionary with `status` and `message`.
    """
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
    """
    OpenFaaS entry point function that handles a JSON request containing 
    username, password, and TOTP code.

    Parameters
    ----------
    req : str
        A JSON-formatted string with 'username', 'password', and '2fa_code'.

    Returns
    -------
    str
        A JSON-formatted response indicating success or failure.
    """
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
