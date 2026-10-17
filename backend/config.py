"""All settings in one place. Values come from environment variables or a local .env file."""

import os

from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI") or "mongodb://localhost:27017"
MONGO_DB = os.getenv("MONGO_DB") or "clothstore"
UPLOAD_DIR = os.getenv("UPLOAD_DIR") or "uploads"
MAX_UPLOAD_BYTES = int(os.getenv("MAX_UPLOAD_MB") or 5) * 1024 * 1024


# if "__main__" == __name__:
#     print(MONGO_DB, MONGO_URI)