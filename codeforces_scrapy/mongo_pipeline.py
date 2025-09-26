# # ...existing code...
# import os
# from pymongo import MongoClient, ASCENDING
# from pymongo.errors import PyMongoError
# from scrapy.exceptions import NotConfigured

# class MongoPipeline:
#     def __init__(self, uri, db, collection):
#         self.uri = uri
#         self.db_name = db
#         self.collection_name = collection
#         self.client = None
#         self.db = None
#         self.col = None
#         self.connected = False

#     @classmethod
#     def from_crawler(cls, crawler):
#         # prefer settings (from settings.py after load_dotenv), fallback to env
#         uri = (
#             crawler.settings.get("MONGO_URI")
#             or crawler.settings.get("MONGODB_URI")
#             or os.getenv("MONGO_URI")
#             or os.getenv("MONGODB_URI")
#         )
#         db = (
#             crawler.settings.get("MONGO_DATABASE")
#             or crawler.settings.get("MONGODB_DB")
#             or os.getenv("MONGO_DATABASE")
#             or os.getenv("MONGODB_DB")
#             or "codeforces"
#         )
#         collection = (
#             crawler.settings.get("MONGO_COLLECTION")
#             or crawler.settings.get("MONGODB_COLLECTION")
#             or os.getenv("MONGO_COLLECTION")
#             or os.getenv("MONGODB_COLLECTION")
#             or "problems"
#         )
#         if not uri:
#             raise NotConfigured("MONGO_URI / MONGODB_URI not set")
#         return cls(uri, db, collection)

#     def open_spider(self, spider):
#         spider.logger.info(f"MongoPipeline: attempting connect to {self.uri.split('@')[-1] if '@' in self.uri else self.uri}")
#         try:
#             self.client = MongoClient(self.uri, serverSelectionTimeoutMS=5000, connectTimeoutMS=5000)
#             self.client.admin.command("ping")
#             self.db = self.client[self.db_name]
#             self.col = self.db[self.collection_name]
#             try:
#                 self.col.create_index([("contest_id", ASCENDING), ("index", ASCENDING)], unique=True)
#             except Exception:
#                 spider.logger.warning("Could not create unique index")
#             self.connected = True
#             spider.logger.info("MongoPipeline: connected and ready")
#         except PyMongoError as e:
#             self.connected = False
#             spider.logger.error(f"MongoPipeline: connection failed: {e}. Items will NOT be stored. To fix: ensure .env or env var MONGODB_URI is set and Atlas whitelist allows your IP.")
# # ...existing code...
# ...existing code...
import os
from pymongo import MongoClient, ASCENDING
from pymongo.errors import PyMongoError
from scrapy.exceptions import NotConfigured

class MongoPipeline:
    def __init__(self, uri, db, collection):
        self.uri = uri
        self.db_name = db
        self.collection_name = collection
        self.client = None
        self.db = None
        self.col = None
        self.connected = False
        self._written = 0
        self._skipped = 0

    @classmethod
    def from_crawler(cls, crawler):
        # prefer settings (settings.py loads .env) then environment
        uri = (
            crawler.settings.get("MONGO_URI")
            or crawler.settings.get("MONGODB_URI")
            or os.getenv("MONGO_URI")
            or os.getenv("MONGODB_URI")
        )
        db = (
            crawler.settings.get("MONGO_DATABASE")
            or os.getenv("MONGO_DATABASE")
            or os.getenv("MONGODB_DB")
            or "codeforces"
        )
        collection = (
            crawler.settings.get("MONGO_COLLECTION")
            or os.getenv("MONGO_COLLECTION")
            or os.getenv("MONGODB_COLLECTION")
            or "problems"
        )
        if not uri:
            raise NotConfigured("MONGO_URI / MONGODB_URI not set")
        return cls(uri, db, collection)

    def open_spider(self, spider):
        spider.logger.info(f"MongoPipeline: attempting connect to {self.uri.split('@')[-1] if '@' in self.uri else self.uri}")
        try:
            # short timeouts so spider fails fast if unreachable
            self.client = MongoClient(self.uri, serverSelectionTimeoutMS=5000, connectTimeoutMS=5000)
            # verify
            self.client.admin.command("ping")
            self.db = self.client[self.db_name]
            self.col = self.db[self.collection_name]
            try:
                self.col.create_index([("contest_id", ASCENDING), ("index", ASCENDING)], unique=True)
            except Exception:
                spider.logger.debug("MongoPipeline: index creation warning/ignored")
            self.connected = True
            spider.logger.info("MongoPipeline: connected and ready")
        except PyMongoError as e:
            self.connected = False
            spider.logger.error(f"MongoPipeline: connection failed: {e}. Items will NOT be stored.")

    def close_spider(self, spider):
        try:
            if self.client:
                self.client.close()
        finally:
            spider.logger.info(f"MongoPipeline: finished. written={self._written}, skipped={self._skipped}")

    def process_item(self, item, spider):
        if not self.connected:
            self._skipped += 1
            spider.logger.debug("MongoPipeline: skipping DB write (not connected)")
            return item
        query = {"contest_id": item.get("contest_id"), "index": item.get("index")}
        doc = dict(item)
        try:
            res = self.col.update_one(query, {"$set": doc}, upsert=True)
            # increment counter (upserted_id or matched_count)
            self._written += 1
            if res.upserted_id:
                spider.logger.debug(f"MongoPipeline: upserted id {res.upserted_id}")
            return item
        except PyMongoError as e:
            self._skipped += 1
            spider.logger.error(f"MongoPipeline: write failed for {query}: {e}")
            return item
# ...existing code...