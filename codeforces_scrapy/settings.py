# ...existing code...
import os

BOT_NAME = "codeforces_scrapy"

SPIDER_MODULES = ["codeforces_scrapy.spiders"]
NEWSPIDER_MODULE = "codeforces_scrapy.spiders"

# Be polite; override if needed
USER_AGENT = os.getenv("USER_AGENT", "codeforces-scraper/1.0 (+https://github.com/)")

# Disable robots to allow API access (set True if you prefer obeying robots.txt)
ROBOTSTXT_OBEY = False

# Pipelines
ITEM_PIPELINES = {
    "codeforces_scrapy.mongo_pipeline.MongoPipeline": 300,
}

# load .env so Scrapy process sees MONGODB_URI
try:
    from dotenv import load_dotenv
    load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))
except Exception:
    pass 

MONGO_URI = os.getenv("MONGO_URI") or os.getenv("MONGODB_URI") or os.getenv("MONGODB_URI".upper())
MONGO_DATABASE = os.getenv("MONGO_DATABASE", os.getenv("MONGODB_DB", "codeforces"))
MONGO_COLLECTION = os.getenv("MONGO_COLLECTION", os.getenv("MONGODB_COLLECTION", "problems"))
# ...existing code...