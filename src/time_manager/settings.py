import os
import pathlib

db = os.path.join(pathlib.Path(__file__).parent.absolute(), "tmp.db")

DB_URL = os.environ.get("DB_URL", f"sqlite:///{db}")
SCHEME = os.environ.get("SCHEME", "http")
HOST = os.environ.get("HOST", "localhost")
PORT = os.environ.get("PORT", "8000")
