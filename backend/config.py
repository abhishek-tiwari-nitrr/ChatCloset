"""All settings in one place. Values come from environment variables or a local .env file."""

import os

from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI") or "mongodb://localhost:27017"
MONGO_DB = os.getenv("MONGO_DB") or "clothstore"


# if "__main__" == __name__:
#     print(MONGO_DB, MONGO_URI)