# ...existing code...
import os
from dotenv import load_dotenv
from pymongo import MongoClient

# load project .env (project root)
ROOT = os.path.dirname(os.path.dirname(__file__))
load_dotenv(os.path.join(ROOT, ".env"))

uri = os.getenv("MONGODB_URI")
print("Using MONGODB_URI:", ("<hidden>" if uri else "MONGODB_URI not set"))
try:
    client = MongoClient(uri, serverSelectionTimeoutMS=5000)
    info = client.server_info()
    print("Connected. Mongo version:", info.get("version"))
    client.close()
except Exception as e:
    print("Connection failed:", type(e).__name__, e)
# ...existing code...