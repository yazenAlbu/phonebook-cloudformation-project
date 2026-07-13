import os

import pymysql
from dotenv import load_dotenv
from flask import Flask, render_template, request


# Load variables from the local .env file.
load_dotenv()


# Create the Flask application.
app = Flask(__name__)


# General application settings.
DEVELOPER_NAME = os.getenv("DEVELOPER_NAME", "Yazen Albu")
APP_PORT = int(os.getenv("APP_PORT", "5000"))
FLASK_DEBUG = os.getenv("FLASK_DEBUG", "false").lower() == "true"


# MySQL database settings.
DB_CONFIG = {
    "host": os.getenv("DB_HOST", "127.0.0.1"),
    "port": int(os.getenv("DB_PORT", "3306")),
    "user": os.getenv("DB_USER", "phonebook_user"),
    "password": os.getenv("DB_PASSWORD", ""),
    "database": os.getenv("DB_NAME", "phonebook_db"),
    "charset": "utf8mb4",
    "cursorclass": pymysql.cursors.DictCursor,
    "autocommit": True,
    "connect_timeout": 5,
}


def get_db_connection():
    """Create and return a new MySQL connection."""
    return pymysql.connect(**DB_CONFIG)


def find_persons(keyword):
    """Find phonebook records containing the supplied name."""
    search_value = f"%{keyword.strip().lower()}%"
    connection = get_db_connection()

    try:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT id, name, number
                FROM phonebook
                WHERE LOWER(name) LIKE %s
                ORDER BY name;
                """,
                (search_value,),
            )

            records = cursor.fetchall()

            return [
                {
                    "id": record["id"],
                    "name": record["name"].strip().title(),
                    "number": record["number"],
                }
                for record in records
            ]
    finally:
        connection.close()


@app.route("/", methods=["GET", "POST"])
def home():
    """Display the search page and process search requests."""
    if request.method == "POST":
        keyword = request.form.get("username", "").strip()

        if not keyword:
            return render_template(
                "index.html",
                results=[],
                show_result=False,
                error_message="Please enter a name to search.",
                developer_name=DEVELOPER_NAME,
            )

        try:
            results = find_persons(keyword)
        except pymysql.MySQLError:
            app.logger.exception("Database search failed.")

            return render_template(
                "index.html",
                results=[],
                show_result=False,
                error_message="Could not connect to the phonebook database.",
                developer_name=DEVELOPER_NAME,
            )

        return render_template(
            "index.html",
            results=results,
            searched_keyword=keyword,
            show_result=True,
            error_message=None,
            developer_name=DEVELOPER_NAME,
        )

    return render_template(
        "index.html",
        results=[],
        show_result=False,
        error_message=None,
        developer_name=DEVELOPER_NAME,
    )


@app.route("/health")
def health():
    """Return the application health status."""
    return {"status": "healthy"}, 200


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=APP_PORT,
        debug=FLASK_DEBUG,
    )