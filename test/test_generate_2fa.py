import importlib.util
import os
import sys
import json
import tempfile
import shutil
from unittest import mock

# Set up safe QR_DIR
temp_qr_dir = tempfile.mkdtemp()

# Load handler
handler_path = os.path.abspath("generate-2fa/handler.py")
spec = importlib.util.spec_from_file_location("generate_2fa", handler_path)
generate_2fa = importlib.util.module_from_spec(spec)
sys.modules["generate_2fa"] = generate_2fa
generate_2fa.QR_DIR = temp_qr_dir

# Disable real directory creation
original_makedirs = os.makedirs
os.makedirs = lambda path, exist_ok=False: None
spec.loader.exec_module(generate_2fa)
os.makedirs = original_makedirs  # restore

# -------------------- TESTS --------------------

@mock.patch.dict(os.environ, {
    "DB_HOST": "localhost",
    "DB_USER": "user",
    "DB_PASSWORD": "pass",
    "DB_NAME": "test_db",
    "REQUEST_METHOD": "POST" 
})
@mock.patch("generate_2fa.pymysql.connect")
@mock.patch("generate_2fa.qrcode.make")
@mock.patch("generate_2fa.make_response")
def test_generate_2fa_success(mock_make_response, mock_qrcode_make, mock_connect):
    # Simulate DB behavior
    mock_conn = mock.MagicMock()
    mock_cursor = mock.MagicMock()
    mock_connect.return_value = mock_conn
    mock_conn.__enter__.return_value = mock_conn
    mock_conn.cursor.return_value.__enter__.return_value = mock_cursor

    # Simulate QR code generation
    mock_img = mock.MagicMock()
    mock_img.save.return_value = None
    mock_qrcode_make.return_value = mock_img

    # Simulate response building
    mock_resp = mock.Mock()
    mock_resp.headers = {}
    mock_make_response.return_value = mock_resp

    request_data = json.dumps({"username": "testuser"})
    response = generate_2fa.handle(request_data)

    # Assertions
    mock_make_response.assert_called()
    assert "Access-Control-Allow-Origin" in mock_resp.headers

# -------------------- CLEANUP --------------------

def teardown_module(module):
    shutil.rmtree(temp_qr_dir)
