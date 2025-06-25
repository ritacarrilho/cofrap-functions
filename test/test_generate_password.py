import importlib.util
import os
import tempfile
import shutil
import sys
import json
from unittest import mock

# Create a temporary directory for QR codes
temp_dir = tempfile.mkdtemp()

# Prepare import without executing it yet
handler_path = os.path.abspath("generate-password/handler.py")
spec = importlib.util.spec_from_file_location("generate_password", handler_path)
generate_password = importlib.util.module_from_spec(spec)

# Inject safe QR_DIR BEFORE loading module
sys.modules["generate_password"] = generate_password
generate_password.QR_DIR = temp_dir

# Patch os.makedirs to skip the unsafe call inside the module
original_makedirs = os.makedirs
os.makedirs = lambda path, exist_ok=False: None
spec.loader.exec_module(generate_password)

# Restore os.makedirs for normal usage
os.makedirs = original_makedirs

# -------------------- TESTS --------------------

def test_generate_strong_password_length():
    password = generate_password.generate_strong_password()
    assert len(password) == 24
    assert any(c.isdigit() for c in password)
    assert any(c.isalpha() for c in password)

@mock.patch.dict(os.environ, {
    "DB_HOST": "localhost",
    "DB_USER": "test",
    "DB_PASSWORD": "test",
    "DB_NAME": "test_db"
})
@mock.patch("generate_password.pymysql.connect")
@mock.patch("generate_password.qrcode.make")
@mock.patch("generate_password.make_response")
def test_handle_success(mock_make_response, mock_qrcode, mock_connect):
    # Setup mocks
    mock_conn = mock.MagicMock()
    mock_cursor = mock.MagicMock()
    mock_connect.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cursor
    mock_cursor.fetchone.return_value = None 

    # Fake QR
    mock_qr = mock.MagicMock()
    mock_qrcode.return_value = mock_qr
    mock_qr.save.return_value = None

    # Mock request and response
    mock_request = mock.Mock()
    mock_request.method = "POST"

    fake_response = mock.Mock()
    fake_response.headers = {}
    mock_make_response.return_value = fake_response

    with mock.patch("generate_password.request", mock_request):
        resp = generate_password.handle(json.dumps({"username": "testuser"}))

    # Assertions
    assert resp.headers["Access-Control-Allow-Origin"] == "*"
    mock_make_response.assert_called()


@mock.patch("generate_password.make_response")
def test_handle_missing_username(mock_make_response):
    req_data = json.dumps({})
    mock_request = mock.Mock()
    mock_request.method = "POST"

    with mock.patch("generate_password.request", mock_request):
        resp = generate_password.handle(req_data)
        mock_make_response.assert_called()
        response_body = mock_make_response.call_args[0][0]
        assert "username is required" in response_body


@mock.patch("generate_password.make_response")
def test_handle_invalid_json(mock_make_response):
    mock_request = mock.Mock()
    mock_request.method = "POST"

    with mock.patch("generate_password.request", mock_request):
        resp = generate_password.handle("INVALID_JSON")
        mock_make_response.assert_called()
        response_body = mock_make_response.call_args[0][0]
        assert "status" in response_body

# -------------------- CLEANUP --------------------


def teardown_module(module):
    shutil.rmtree(temp_dir)
