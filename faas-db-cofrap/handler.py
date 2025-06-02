import os
import mysql.connector

def handle(req):
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