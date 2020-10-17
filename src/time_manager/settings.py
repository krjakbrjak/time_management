import os
import pathlib

db = os.path.join(pathlib.Path(__file__).parent.absolute(), "tmp.db")

DB_URL = os.environ.get("DB_URL", f"sqlite:///{db}")
