import importlib.util
import inspect
import os
import builtins

# Map paths to friendly function names
paths = {
    "../generate-password/handler.py": "Generate Password",
    "../generate-2fa/handler.py": "Generate 2FA",
    "../authenticate-user/handler.py": "Authenticate User",
    "../get-users/handler.py": "Get all users Function",
}

def extract_doc(file_path, title):
    # Patch os.makedirs to no-op during import
    original_makedirs = os.makedirs
    os.makedirs = lambda path, exist_ok=False: None

    try:
        spec = importlib.util.spec_from_file_location("handler", file_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
    finally:
        os.makedirs = original_makedirs  # Restore original

    docs = f"# {title}\n\n"
    for name, obj in inspect.getmembers(module):
        if inspect.isfunction(obj):
            docs += f"## `{name}`\n\n"
            docs += (inspect.getdoc(obj) or "No docstring found.") + "\n\n---\n\n"
    return docs

with open("functions_doc.md", "w") as out:
    for path, title in paths.items():
        out.write(extract_doc(path, title))