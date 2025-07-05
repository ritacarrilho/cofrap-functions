import importlib.util
import os
import sys
import time
import pytest
from unittest import mock

# Define the path to the authenticate-user handler
handler_path = os.path.abspath("authenticate-user/handler.py")

# Prepare import spec and load module
spec = importlib.util.spec_from_file_location("authenticate_user", handler_path)
authenticate_user = importlib.util.module_from_spec(spec)
sys.modules["authenticate_user"] = authenticate_user
spec.loader.exec_module(authenticate_user)

# ---------------------- TEST ----------------------


def test_decode_b64():
    original = "my_secure_value"
    encoded = "bXlfc2VjdXJlX3ZhbHVl" 
    result = authenticate_user.decode_b64(encoded)
    assert result == original


def test_decode_b64_invalid():
    invalid_b64 = "!!not-base64@@"

    with pytest.raises(Exception):
        authenticate_user.decode_b64(invalid_b64)


def test_is_expired_true():
    # Create a timestamp 7 months ago
    old_timestamp = int(time.time()) - (7 * 30 * 24 * 60 * 60)
    assert authenticate_user.is_expired(old_timestamp) == True


def test_is_expired_false():
    # Create a timestamp 2 months ago
    recent_timestamp = int(time.time()) - (2 * 30 * 24 * 60 * 60)
    assert authenticate_user.is_expired(recent_timestamp) == False


def test_is_expired_edge_case():
    # Exactly 6 months ago should not yet be expired
    exact_six_months = int(time.time()) - (6 * 30 * 24 * 60 * 60)
    assert authenticate_user.is_expired(exact_six_months) == False


@mock.patch.dict('os.environ', {
    'DB_HOST': 'localhost',
    'DB_USER': 'test_user',
    'DB_PASSWORD': 'test_pass',
    'DB_NAME': 'test_db'
})
@mock.patch("authenticate_user.pymysql.connect")
def test_fetch_user(mock_connect):
    # Set up mocks
    mock_conn = mock.MagicMock()
    mock_cursor = mock.MagicMock()

    mock_connect.return_value = mock_conn
    mock_conn.__enter__.return_value = mock_conn
    mock_conn.cursor.return_value.__enter__.return_value = mock_cursor

    # Simulate DB return
    expected_user = ("enc_pwd", "enc_mfa", 1234567890, 0)
    mock_cursor.fetchone.return_value = expected_user

    # Execute function
    result = authenticate_user.fetch_user("testuser")

    # Assert
    assert result == expected_user
    mock_cursor.execute.assert_called_once_with(
        "SELECT password, mfa, gendate, expired FROM users WHERE username = %s",
        ("testuser",)
    )


@mock.patch.dict(os.environ, {
    "DB_HOST": "localhost",
    "DB_USER": "test_user",
    "DB_PASSWORD": "test_pass",
    "DB_NAME": "test_db"
})
@mock.patch("authenticate_user.pymysql.connect")
def test_mark_expired(mock_connect):
    mock_conn = mock.MagicMock()
    mock_cursor = mock.MagicMock()

    mock_connect.return_value = mock_conn
    mock_conn.__enter__.return_value = mock_conn
    mock_conn.cursor.return_value.__enter__.return_value = mock_cursor

    # Call function
    authenticate_user.mark_expired("testuser")

    # Assert SQL command was run with correct parameters
    mock_cursor.execute.assert_called_once_with(
        "UPDATE users SET expired = 1 WHERE username = %s", ("testuser",)
    )
    mock_conn.commit.assert_called_once()


@mock.patch("authenticate_user.decode_b64")
@mock.patch("authenticate_user.fetch_user")
@mock.patch("authenticate_user.is_expired", return_value=False)
@mock.patch("authenticate_user.pyotp.TOTP")
def test_authenticate_user_success(mock_totp_cls, mock_is_expired, mock_fetch_user, mock_decode):
    mock_fetch_user.return_value = ("enc_pwd", "enc_mfa", 1234567890, 0)
    mock_decode.side_effect = ["realpass", "secret"]

    mock_totp = mock.Mock()
    mock_totp.verify.return_value = True
    mock_totp_cls.return_value = mock_totp

    result = authenticate_user.authenticate_user("testuser", "realpass", "123456")
    assert result == {"status": "success", "message": "Authentication successful"}
