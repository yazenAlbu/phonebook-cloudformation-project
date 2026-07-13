import os

from dotenv import load_dotenv
from flask import Flask, render_template


# Load environment variables from the local .env file.
load_dotenv()


# Create the Flask application.
app = Flask(__name__)


# Read application settings from environment variables.
DEVELOPER_NAME = os.getenv("DEVELOPER_NAME", "Yazen Albu")
APP_PORT = int(os.getenv("APP_PORT", "5000"))
FLASK_DEBUG = os.getenv("FLASK_DEBUG", "false").lower() == "true"


@app.route("/")
def home():
    """Display the main phonebook page."""
    return render_template(
        "index.html",
        show_result=False,
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