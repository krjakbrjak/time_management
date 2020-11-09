import os
import pathlib

DB_CONFIG = os.environ.get(
    "DB_CONFIG_PATH",
    os.path.join(pathlib.Path(__file__).parent.absolute(), ".dbconfig.json"),
)

SCHEME = os.environ.get("SCHEME", "http")
HOST = os.environ.get("HOST", "localhost")
PORT = os.environ.get("PORT", "8000")
