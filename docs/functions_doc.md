# Generate Password

## `add_cors_headers`

No docstring found.

---

## `generate_strong_password`

No docstring found.

---

## `handle`

Generate a strong password for a user, store it in the database (encoded),
and return a QR code representing the password in base64 format.

This function handles CORS preflight requests and JSON POST requests with a `username`.
If the user already exists, their password is updated; otherwise, a new user is created.

Parameters
----------
req : str
    A JSON-formatted string with the field:
    - `username` (str): the username for which to generate or update a password.

Returns
-------
JSON response
    If successful:
    {
        "status": "ok",
        "qr_code_base64": "<base64-encoded QR code PNG for the password>"
    }

    If error:
    {
        "status": "error",
        "message": "<error message>"
    }

Notes
-----
- A strong password is randomly generated using letters, digits, and punctuation.
- The password is encoded in Base64 and stored in the `password` field of the `users` table.
- The QR code is saved to `QR_DIR/<username>_pwd_qr.png` and returned as a base64 string.
- The function supports updating an existing user or creating a new one.

---

## `make_response`

Sometimes it is necessary to set additional headers in a view.  Because
views do not have to return response objects but can return a value that
is converted into a response object by Flask itself, it becomes tricky to
add headers to it.  This function can be called instead of using a return
and you will get a response object which you can use to attach headers.

If view looked like this and you want to add a new header::

    def index():
        return render_template('index.html', foo=42)

You can now do something like this::

    def index():
        response = make_response(render_template('index.html', foo=42))
        response.headers['X-Parachutes'] = 'parachutes are cool'
        return response

This function accepts the very same arguments you can return from a
view function.  This for example creates a response with a 404 error
code::

    response = make_response(render_template('not_found.html'), 404)

The other use case of this function is to force the return value of a
view function into a response which is helpful with view
decorators::

    response = make_response(view_function())
    response.headers['X-Parachutes'] = 'parachutes are cool'

Internally this function does the following things:

-   if no arguments are passed, it creates a new response argument
-   if one argument is passed, :meth:`flask.Flask.make_response`
    is invoked with it.
-   if more than one argument is passed, the arguments are passed
    to the :meth:`flask.Flask.make_response` function as tuple.

.. versionadded:: 0.6

---

# Generate 2FA

## `add_cors_headers`

No docstring found.

---

## `handle`

Generate a TOTP-based MFA secret for a user, encode it as a QR code,
store the Base64-encoded secret in the database, and return the QR code as base64.

This function handles CORS preflight requests and JSON POST requests with a `username`.

Parameters
----------
req : str
    A JSON-formatted string with the field:
    - `username` (str): the username for whom the MFA secret is generated.

Returns
-------
JSON response
    If successful:
    {
        "code_mfa": "<base64-encoded QR code PNG>",
        "status": "ok"
    }

    If error:
    {
        "status": "error",
        "message": "<error details>"
    }

Notes
-----
- The TOTP secret is generated using `pyotp.random_base32()`
- The Base64-encoded secret is saved in the `mfa` field of the `users` table
- The QR code is saved locally as a PNG file at `QR_DIR/<username>_2fa.png`
- The QR code can be scanned by authenticator apps like Google Authenticator

---

## `make_response`

Sometimes it is necessary to set additional headers in a view.  Because
views do not have to return response objects but can return a value that
is converted into a response object by Flask itself, it becomes tricky to
add headers to it.  This function can be called instead of using a return
and you will get a response object which you can use to attach headers.

If view looked like this and you want to add a new header::

    def index():
        return render_template('index.html', foo=42)

You can now do something like this::

    def index():
        response = make_response(render_template('index.html', foo=42))
        response.headers['X-Parachutes'] = 'parachutes are cool'
        return response

This function accepts the very same arguments you can return from a
view function.  This for example creates a response with a 404 error
code::

    response = make_response(render_template('not_found.html'), 404)

The other use case of this function is to force the return value of a
view function into a response which is helpful with view
decorators::

    response = make_response(view_function())
    response.headers['X-Parachutes'] = 'parachutes are cool'

Internally this function does the following things:

-   if no arguments are passed, it creates a new response argument
-   if one argument is passed, :meth:`flask.Flask.make_response`
    is invoked with it.
-   if more than one argument is passed, the arguments are passed
    to the :meth:`flask.Flask.make_response` function as tuple.

.. versionadded:: 0.6

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

# Get all users Function

## `handle`

Retrieves all user entries from the `users` table in the MariaDB database.

This function connects to the database using credentials provided in environment variables.
It fetches all rows from the `users` table and returns them as a JSON-formatted string.
It uses `DictCursor` to ensure that each row is returned as a dictionary.

Returns
-------
str
    A JSON-formatted string representing a list of users with all their fields.
    If an error occurs (e.g., connection failure, SQL error), a JSON object with an "error" message is returned.

Notes
-----
- The function assumes the table `users` exists and contains the expected schema.
- Ensure that the environment variables `DB_HOST`, `DB_USER`, `DB_PASSWORD`, and `DB_NAME` are set.
- This function is useful for debugging or admin purposes and should be secured in a real-world deployment.

---

