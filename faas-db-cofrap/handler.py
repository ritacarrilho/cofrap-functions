import os
import mysql.connector



def handle():
    """
        Connects to the MariaDB database and retrieves the current timestamp.

        This function is designed to be used as a serverless function in OpenFaaS.
        It connects to the database using environment variables for credentials,
        executes a simple SELECT query to get the current time, and returns a confirmation message.

        Returns
        -------
        str
            A string confirming the successful database connection and the current time,
            or an error message in case of failure.
    """
    try:
        conn = mysql.connector.connect(
            host=os.getenv("DB_HOST"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            database=os.getenv("DB_NAME")
        )

        cursor = conn.cursor()
        cursor.execute("SELECT NOW();")
        result = cursor.fetchone()
        cursor.close()
        conn.close()

        return f"Connexion réussie à MariaDB ! Heure : {result[0]}"
    except Exception as e:
        return f"Erreur : {str(e)}"