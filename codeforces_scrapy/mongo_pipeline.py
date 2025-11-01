import os
from pymongo import MongoClient, ASCENDING, DESCENDING
from pymongo.errors import PyMongoError, DuplicateKeyError
from scrapy.exceptions import NotConfigured


class EnhancedMongoPipeline:
    """
    Pipeline nâng cao lưu data vào 3 collections:
    - problems: bài toán (upsert by contest_id + index)
    - users: user profiles (upsert by handle)
    - submissions: submissions (INSERT ALL - không dùng unique index)
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
        
        # Batch insert để tăng tốc
        self.submission_batch = []
        self.batch_size = 1000  # Insert 1000 submissions cùng lúc

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
            # ==================== PROBLEMS ====================
            # Unique index: (contest_id, index)
            self.problems_col.create_index(
                [("contest_id", ASCENDING), ("index", ASCENDING)], 
                unique=True
            )
            self.problems_col.create_index([("rating", ASCENDING)])
            self.problems_col.create_index([("solved_count", DESCENDING)])
            self.problems_col.create_index([("tags", ASCENDING)])
            
            # ==================== USERS ====================
            # Unique index: handle
            self.users_col.create_index([("handle", ASCENDING)], unique=True)
            self.users_col.create_index([("rating", DESCENDING)])
            self.users_col.create_index([("country", ASCENDING)])
            
            # ==================== SUBMISSIONS ====================
            # QUAN TRỌNG: KHÔNG tạo unique index cho submission_id
            # Chỉ tạo index thông thường để query nhanh
            
            # XÓA unique index nếu đã tồn tại
            try:
                existing_indexes = self.submissions_col.index_information()
                for index_name, index_info in existing_indexes.items():
                    if 'unique' in index_info and index_info['unique']:
                        spider.logger.info(f"Dropping unique index: {index_name}")
                        self.submissions_col.drop_index(index_name)
            except Exception as e:
                spider.logger.debug(f"Could not drop indexes: {e}")
            
            # Tạo NON-UNIQUE indexes để query nhanh
            self.submissions_col.create_index([("submission_id", ASCENDING)], unique=False)
            self.submissions_col.create_index([("author_handle", ASCENDING)])
            self.submissions_col.create_index([("contest_id", ASCENDING), ("problem_index", ASCENDING)])
            self.submissions_col.create_index([("programming_language", ASCENDING)])
            self.submissions_col.create_index([("verdict", ASCENDING)])
            self.submissions_col.create_index([("creation_time", DESCENDING)])
            
            spider.logger.info("EnhancedMongoPipeline: indexes created successfully")
        except Exception as e:
            spider.logger.warning(f"EnhancedMongoPipeline: index creation warning: {e}")

    def close_spider(self, spider):
        """Flush batch và đóng kết nối"""
        # Insert remaining submissions in batch
        if self.submission_batch:
            self._flush_submission_batch(spider)
        
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
        """Xử lý problem item - UPSERT"""
        query = {"contest_id": item.get("contest_id"), "index": item.get("index")}
        doc = dict(item)
        
        try:
            res = self.problems_col.update_one(query, {"$set": doc}, upsert=True)
            self.stats['problems_written'] += 1
            
            if res.upserted_id:
                spider.logger.debug(f"Problem inserted: {item.get('problem_id')}")
            else:
                spider.logger.debug(f"Problem updated: {item.get('problem_id')}")
            
            return item
        except PyMongoError as e:
            self.stats['problems_skipped'] += 1
            spider.logger.error(f"Problem write failed: {e}")
            return item

    def _process_user(self, item, spider):
        """Xử lý user item - UPSERT"""
        query = {"handle": item.get("handle")}
        doc = dict(item)
        
        try:
            res = self.users_col.update_one(query, {"$set": doc}, upsert=True)
            self.stats['users_written'] += 1
            
            if res.upserted_id:
                spider.logger.debug(f"User inserted: {item.get('handle')}")
            else:
                spider.logger.debug(f"User updated: {item.get('handle')}")
            
            return item
        except PyMongoError as e:
            self.stats['users_skipped'] += 1
            spider.logger.error(f"User write failed: {e}")
            return item

    def _process_submission(self, item, spider):
        """
        Xử lý submission item - INSERT ALL (batch mode)
        Không check duplicate, insert tất cả submissions
        """
        doc = dict(item)
        
        # Add to batch
        self.submission_batch.append(doc)
        
        # Flush batch khi đủ kích thước
        if len(self.submission_batch) >= self.batch_size:
            self._flush_submission_batch(spider)
        
        return item

    def _flush_submission_batch(self, spider):
        """Insert batch submissions vào MongoDB"""
        if not self.submission_batch:
            return
        
        try:
            # INSERT MANY - insert tất cả cùng lúc
            result = self.submissions_col.insert_many(
                self.submission_batch, 
                ordered=False  # Continue on error
            )
            
            inserted_count = len(result.inserted_ids)
            self.stats['submissions_written'] += inserted_count
            
            spider.logger.info(
                f"✅ Batch insert: {inserted_count} submissions "
                f"(Total: {self.stats['submissions_written']})"
            )
            
        except PyMongoError as e:
            # Nếu có lỗi, vẫn cố gắng đếm số bản ghi đã insert thành công
            if hasattr(e, 'details') and 'writeErrors' in e.details:
                inserted_count = e.details.get('nInserted', 0)
                self.stats['submissions_written'] += inserted_count
                spider.logger.warning(
                    f"⚠️ Partial batch insert: {inserted_count}/{len(self.submission_batch)} submissions"
                )
            else:
                self.stats['submissions_skipped'] += len(self.submission_batch)
                spider.logger.error(f"❌ Batch insert failed: {e}")
        
        finally:
            # Clear batch
            self.submission_batch = []


# ==================== ALTERNATIVE: Single Insert Mode ====================
# Nếu batch mode gặp vấn đề, dùng cách này:

class EnhancedMongoPipelineSingleInsert(EnhancedMongoPipeline):
    """
    Alternative pipeline: Insert từng submission một
    Chậm hơn nhưng ổn định hơn
    """
    
    def _process_submission(self, item, spider):
        """Xử lý submission item - INSERT ONE"""
        doc = dict(item)
        
        try:
            # INSERT ONE - không check duplicate
            result = self.submissions_col.insert_one(doc)
            self.stats['submissions_written'] += 1
            
            if self.stats['submissions_written'] % 1000 == 0:
                spider.logger.info(
                    f"✅ Submissions inserted: {self.stats['submissions_written']}"
                )
            
            return item
            
        except PyMongoError as e:
            self.stats['submissions_skipped'] += 1
            spider.logger.error(f"Submission insert failed: {e}")
            return item