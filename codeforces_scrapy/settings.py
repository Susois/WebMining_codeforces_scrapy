import os

BOT_NAME = "codeforces_scrapy"

SPIDER_MODULES = ["codeforces_scrapy.spiders"]
NEWSPIDER_MODULE = "codeforces_scrapy.spiders"

# User agent
USER_AGENT = os.getenv("USER_AGENT", "codeforces-scraper/1.0 (+https://github.com/)")

# Robots.txt
ROBOTSTXT_OBEY = False

# Configure item pipelines
# QUAN TRỌNG: Tên class phải khớp với tên trong file mongo_pipeline.py
ITEM_PIPELINES = {
    "codeforces_scrapy.mongo_pipeline.EnhancedMongoPipeline": 300,
}

# Tăng concurrent requests để crawl nhanh hơn
CONCURRENT_REQUESTS = 8
CONCURRENT_REQUESTS_PER_DOMAIN = 4

# AutoThrottle để tránh bị ban
AUTOTHROTTLE_ENABLED = True
AUTOTHROTTLE_START_DELAY = 1
AUTOTHROTTLE_MAX_DELAY = 3
AUTOTHROTTLE_TARGET_CONCURRENCY = 2.0

# Load .env file
try:
    from dotenv import load_dotenv
    load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))
except Exception:
    pass 

# MongoDB settings
MONGO_URI = os.getenv("MONGO_URI") or os.getenv("MONGODB_URI")
MONGO_DATABASE = os.getenv("MONGO_DATABASE", os.getenv("MONGODB_DB", "codeforces"))
MONGO_COLLECTION = os.getenv("MONGO_COLLECTION", os.getenv("MONGODB_COLLECTION", "problems"))

# Request settings để tránh bị ban
CONCURRENT_REQUESTS = 16
DOWNLOAD_DELAY = 1
AUTOTHROTTLE_ENABLED = True
AUTOTHROTTLE_START_DELAY = 1
AUTOTHROTTLE_MAX_DELAY = 10