import importlib.util
import os
import sys
import json
from unittest import mock

# Load the handler module safely
handler_path = os.path.abspath("get-users/handler.py")
spec = importlib.util.spec_from_file_location("get_users", handler_path)
get_users = importlib.util.module_from_spec(spec)
sys.modules["get_users"] = get_users
spec.loader.exec_module(get_users)

# -------------------- TESTS --------------------

@mock.patch.dict(os.environ, {
    "DB_HOST": "localhost",
    "DB_USER": "test",
    "DB_PASSWORD": "test",
    "DB_NAME": "test_db"
})
@mock.patch("get_users.pymysql.connect")
def test_get_users_success(mock_connect):
    # Mock DB connection and cursor
    mock_conn = mock.MagicMock()
    mock_cursor = mock.MagicMock()
    mock_connect.return_value = mock_conn
    mock_conn.__enter__.return_value = mock_conn
    mock_conn.cursor.return_value.__enter__.return_value = mock_cursor

    # Simulate DB rows
    mock_rows = [
        {"username": "alice", "password": "x", "mfa": "y"},
        {"username": "bob", "password": "a", "mfa": "b"}
    ]
    mock_cursor.fetchall.return_value = mock_rows

    # Call handler
    result = get_users.handle(None)

    # Verify output
    parsed = json.loads(result)
    assert isinstance(parsed, list)
    assert parsed[0]["username"] == "alice"
    assert parsed[1]["username"] == "bob"
