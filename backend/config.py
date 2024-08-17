import os
import psycopg2
from flask import Flask
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# PostgreSQL connection details
DB_NAME = os.environ.get("DB_NAME_SPOTIFY", "mydatabase")
DB_USER = os.environ.get("DB_USER_SPOTIFY", "myuser")
DB_PASSWORD = os.environ.get("DB_PASSWORD_SPOTIFY", "mypassword")
DB_HOST = os.environ.get("DB_HOST", "localhost")
DB_PORT = os.environ.get("DB_PORT", "5432")

# Connection string
DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

app.secret_key = os.environ.get("FLASK_SECRET_KEY")


def get_db_connection():
    conn = psycopg2.connect(DATABASE_URL)
    return conn
