import pymysql
import json
import os

def handle(req):
    """
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
    """
    try:
        connection = pymysql.connect(
            host=os.environ['DB_HOST'],
            user=os.environ['DB_USER'],
            password=os.environ['DB_PASSWORD'],
            database=os.environ['DB_NAME'],
            cursorclass=pymysql.cursors.DictCursor
        )

        with connection:
            with connection.cursor() as cursor:
                cursor.execute("SELECT * FROM users")
                rows = cursor.fetchall()
                return json.dumps(rows, indent=2)

    except Exception as e:
        return json.dumps({ "error": str(e) })