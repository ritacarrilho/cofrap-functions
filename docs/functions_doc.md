# Generate Password

## `generate_strong_password`

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

---

## `handle`

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

---

# Generate 2FA

## `handle`

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

---

# Authenticate User

## `authenticate_user`

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

---

## `decode_b64`

Decode a base64-encoded string.

Parameters
----------
value : str
    A base64-encoded string.

Returns
-------
str
    The decoded plaintext string.

---

## `fetch_user`

Retrieve user details from the database.

Parameters
----------
username : str
    The username whose data needs to be fetched.

Returns
-------
tuple or None
    A tuple containing (password, mfa, gendate, expired) or None if user is not found.

---

## `get_db_connection`

Establish a connection to the MariaDB database using credentials 
and host information from environment variables.

Returns
-------
pymysql.Connection
    An active connection object to the MariaDB database.

---

## `handle`

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

---

## `is_expired`

Check whether the credentials are older than 6 months.

Parameters
----------
gendate_timestamp : int
    Timestamp indicating when the credentials were generated.

Returns
-------
bool
    True if credentials are expired, False otherwise.

---

## `mark_expired`

Update the user’s status to 'expired' in the database.

Parameters
----------
username : str
    The username to be marked as expired.

---

# DB Test Function

## `handle`

Connects to the MariaDB database and retrieves the current timestamp.

This function is designed to be used as a serverless function in OpenFaaS.
It connects to the database using environment variables for credentials,
executes a simple SELECT query to get the current time, and returns a confirmation message.

Returns
-------
str
    A string confirming the successful database connection and the current time,
    or an error message in case of failure.

---

