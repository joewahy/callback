from flask import Flask
from dotenv import load_dotenv
import os

from . import db

load_dotenv()

app = Flask(__name__, template_folder="../templates", static_folder="../static")
app.secret_key = os.environ.get("SECRET_KEY")
if not app.secret_key:
    raise RuntimeError("SECRET_KEY environment variable is not set")

db.app_create()

from . import auth, dashboard  # noqa: E402  (registers routes on `app`)
