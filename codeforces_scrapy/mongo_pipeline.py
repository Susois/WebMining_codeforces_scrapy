import os
from pymongo import MongoClient, ASCENDING, DESCENDING
from pymongo.errors import PyMongoError
from scrapy.exceptions import NotConfigured


class EnhancedMongoPipeline:
    """
    Pipeline nâng cao lưu data vào 3 collections:
    - problems: bài toán
    - users: user profiles
    - submissions: submissions
    """
    
    def __init__(self, uri, db_name):
        self.uri = uri
        self.db_name = db_name
        self.client = None
        self.db = None
        self.problems_col = None
        self.users_col = None
        self.submissions_col = None
        self.connected = False
        
        # Counters
        self.stats = {
            'problems_written': 0,
            'problems_skipped': 0,
            'users_written': 0,
            'users_skipped': 0,
            'submissions_written': 0,
            'submissions_skipped': 0,
        }

    @classmethod
    def from_crawler(cls, crawler):
        uri = (
            crawler.settings.get("MONGO_URI")
            or crawler.settings.get("MONGODB_URI")
            or os.getenv("MONGO_URI")
            or os.getenv("MONGODB_URI")
        )
        db_name = (
            crawler.settings.get("MONGO_DATABASE")
            or os.getenv("MONGO_DATABASE")
            or os.getenv("MONGODB_DB")
            or "codeforces"
        )
        if not uri:
            raise NotConfigured("MONGO_URI / MONGODB_URI not set")
        return cls(uri, db_name)

    def open_spider(self, spider):
        """Kết nối MongoDB và tạo indexes"""
        spider.logger.info(f"EnhancedMongoPipeline: connecting to MongoDB...")
        try:
            self.client = MongoClient(
                self.uri, 
                serverSelectionTimeoutMS=5000, 
                connectTimeoutMS=5000
            )
            self.client.admin.command("ping")
            self.db = self.client[self.db_name]
            
            # Tạo 3 collections
            self.problems_col = self.db["problems"]
            self.users_col = self.db["users"]
            self.submissions_col = self.db["submissions"]
            
            # Tạo indexes
            self._create_indexes(spider)
            
            self.connected = True
            spider.logger.info("EnhancedMongoPipeline: connected successfully")
            
        except PyMongoError as e:
            self.connected = False
            spider.logger.error(f"EnhancedMongoPipeline: connection failed: {e}")

    def _create_indexes(self, spider):
        """Tạo indexes cho các collections"""
        try:
            # Problems indexes
            self.problems_col.create_index(
                [("contest_id", ASCENDING), ("index", ASCENDING)], 
                unique=True
            )
            self.problems_col.create_index([("rating", ASCENDING)])
            self.problems_col.create_index([("solved_count", DESCENDING)])
            self.problems_col.create_index([("tags", ASCENDING)])
            
            # Users indexes
            self.users_col.create_index([("handle", ASCENDING)], unique=True)
            self.users_col.create_index([("rating", DESCENDING)])
            self.users_col.create_index([("country", ASCENDING)])
            
            # Submissions indexes
            self.submissions_col.create_index([("submission_id", ASCENDING)], unique=True)
            self.submissions_col.create_index([("author_handle", ASCENDING)])
            self.submissions_col.create_index([("contest_id", ASCENDING), ("problem_index", ASCENDING)])
            self.submissions_col.create_index([("programming_language", ASCENDING)])
            self.submissions_col.create_index([("verdict", ASCENDING)])
            self.submissions_col.create_index([("creation_time", DESCENDING)])
            
            spider.logger.info("EnhancedMongoPipeline: indexes created")
        except Exception as e:
            spider.logger.warning(f"EnhancedMongoPipeline: index creation warning: {e}")

    def close_spider(self, spider):
        """Đóng kết nối và log statistics"""
        try:
            if self.client:
                self.client.close()
        finally:
            spider.logger.info("=" * 60)
            spider.logger.info("EnhancedMongoPipeline Statistics:")
            spider.logger.info(f"  Problems: {self.stats['problems_written']} written, {self.stats['problems_skipped']} skipped")
            spider.logger.info(f"  Users: {self.stats['users_written']} written, {self.stats['users_skipped']} skipped")
            spider.logger.info(f"  Submissions: {self.stats['submissions_written']} written, {self.stats['submissions_skipped']} skipped")
            spider.logger.info("=" * 60)

    def process_item(self, item, spider):
        """Route item đến collection tương ứng"""
        if not self.connected:
            spider.logger.debug("EnhancedMongoPipeline: skipping (not connected)")
            return item
        
        item_type = type(item).__name__
        
        if item_type == "CodeforcesProblem":
            return self._process_problem(item, spider)
        elif item_type == "CodeforcesUser":
            return self._process_user(item, spider)
        elif item_type == "CodeforcesSubmission":
            return self._process_submission(item, spider)
        else:
            spider.logger.warning(f"Unknown item type: {item_type}")
            return item

    def _process_problem(self, item, spider):
        """Xử lý problem item"""
        query = {"contest_id": item.get("contest_id"), "index": item.get("index")}
        doc = dict(item)
        
        try:
            res = self.problems_col.update_one(query, {"$set": doc}, upsert=True)
            self.stats['problems_written'] += 1
            return item
        except PyMongoError as e:
            self.stats['problems_skipped'] += 1
            spider.logger.error(f"Problem write failed: {e}")
            return item

    def _process_user(self, item, spider):
        """Xử lý user item"""
        query = {"handle": item.get("handle")}
        doc = dict(item)
        
        try:
            res = self.users_col.update_one(query, {"$set": doc}, upsert=True)
            self.stats['users_written'] += 1
            return item
        except PyMongoError as e:
            self.stats['users_skipped'] += 1
            spider.logger.error(f"User write failed: {e}")
            return item

    def _process_submission(self, item, spider):
        """Xử lý submission item"""
        query = {"submission_id": item.get("submission_id")}
        doc = dict(item)
        
        try:
            res = self.submissions_col.update_one(query, {"$set": doc}, upsert=True)
            self.stats['submissions_written'] += 1
            return item
        except PyMongoError as e:
            self.stats['submissions_skipped'] += 1
            spider.logger.error(f"Submission write failed: {e}")
            return item