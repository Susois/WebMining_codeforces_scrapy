import json
import scrapy
from codeforces_scrapy.items import CodeforcesProblem, CodeforcesUser, CodeforcesSubmission


class CodeforcesEnhancedSpider(scrapy.Spider):
    """
    Spider nâng cao để crawl toàn bộ dữ liệu từ Codeforces API
    Thu thập: problems, users, submissions với đầy đủ thông tin
    """
    name = "codeforces_enhanced"
    allowed_domains = ["codeforces.com"]
    
    custom_settings = {
        'CONCURRENT_REQUESTS': 1,  # Tránh spam API
        'DOWNLOAD_DELAY': 2,  # Delay 2s giữa các request
    }

    def start_requests(self):
        """Bắt đầu với API problemset"""
        yield scrapy.Request(
            url="https://codeforces.com/api/problemset.problems",
            callback=self.parse_problems,
            errback=self.handle_error
        )

    def parse_problems(self, response):
        """Parse problems và statistics"""
        try:
            data = json.loads(response.text)
            if data.get("status") != "OK":
                self.logger.error(f"API problems error: {data.get('comment', 'Unknown')}")
                return

            result = data.get("result", {})
            problems = result.get("problems", [])
            stats = result.get("problemStatistics", [])

            # Build lookup cho solved count
            stats_lookup = {}
            for s in stats:
                key = f"{s.get('contestId')}_{s.get('index')}"
                stats_lookup[key] = s.get("solvedCount", 0)

            self.logger.info(f"Found {len(problems)} problems")

            for p in problems:
                contest_id = p.get("contestId")
                index = p.get("index")
                key = f"{contest_id}_{index}"
                
                item = CodeforcesProblem()
                item["contest_id"] = contest_id
                item["index"] = index
                item["problem_id"] = f"{contest_id}{index}"
                item["title"] = p.get("name")
                item["tags"] = p.get("tags", [])
                item["rating"] = p.get("rating")  # Có thể None
                item["solved_count"] = stats_lookup.get(key, 0)
                item["url"] = f"https://codeforces.com/problemset/problem/{contest_id}/{index}"
                
                # Thêm các trường mới
                item["type"] = p.get("type", "PROGRAMMING")
                item["points"] = p.get("points")
                item["contest_name"] = p.get("contestName")
                
                yield item

            # Sau khi crawl problems, crawl top users
            yield scrapy.Request(
                url="https://codeforces.com/api/user.ratedList?activeOnly=false",
                callback=self.parse_users,
                errback=self.handle_error
            )

        except json.JSONDecodeError as e:
            self.logger.error(f"JSON decode error: {e}")

    def parse_users(self, response):
        """Parse danh sách users"""
        try:
            data = json.loads(response.text)
            if data.get("status") != "OK":
                self.logger.error(f"API users error: {data.get('comment', 'Unknown')}")
                return

            users = data.get("result", [])
            self.logger.info(f"Found {len(users)} users")
            
            # Lấy top users để crawl submissions (có thể giới hạn số lượng)
            top_users = users[:2000]  # Top 2000 users
            
            for user in top_users:
                item = CodeforcesUser()
                item["handle"] = user.get("handle")
                item["rating"] = user.get("rating")
                item["max_rating"] = user.get("maxRating")
                item["rank"] = user.get("rank")
                item["max_rank"] = user.get("maxRank")
                item["country"] = user.get("country")
                item["organization"] = user.get("organization")
                item["contribution"] = user.get("contribution")
                item["friend_of_count"] = user.get("friendOfCount")
                item["registration_time"] = user.get("registrationTimeSeconds")
                
                yield item
                
                # Crawl submissions của user này
                yield scrapy.Request(
                    url=f"https://codeforces.com/api/user.status?handle={item['handle']}&from=1&count=500",
                    callback=self.parse_user_submissions,
                    meta={'handle': item['handle']},
                    errback=self.handle_error
                )

        except json.JSONDecodeError as e:
            self.logger.error(f"JSON decode error: {e}")

    def parse_user_submissions(self, response):
        """Parse submissions của một user"""
        try:
            data = json.loads(response.text)
            if data.get("status") != "OK":
                # User có thể không có submissions hoặc lỗi API
                return

            submissions = data.get("result", [])
            handle = response.meta.get('handle')
            
            self.logger.debug(f"Found {len(submissions)} submissions for {handle}")
            
            for sub in submissions:
                item = CodeforcesSubmission()
                item["submission_id"] = sub.get("id")
                item["contest_id"] = sub.get("contestId")
                item["problem_index"] = sub.get("problem", {}).get("index")
                item["problem_name"] = sub.get("problem", {}).get("name")
                item["programming_language"] = sub.get("programmingLanguage")
                item["verdict"] = sub.get("verdict")
                item["testset"] = sub.get("testset")
                item["passed_test_count"] = sub.get("passedTestCount")
                item["time_consumed_millis"] = sub.get("timeConsumedMillis")
                item["memory_consumed_bytes"] = sub.get("memoryConsumedBytes")
                item["creation_time"] = sub.get("creationTimeSeconds")
                
                # Author info
                author = sub.get("author", {})
                item["author_handle"] = handle
                item["participant_type"] = author.get("participantType")
                
                yield item

        except json.JSONDecodeError as e:
            self.logger.error(f"JSON decode error: {e}")

    def handle_error(self, failure):
        """Xử lý lỗi request"""
        self.logger.error(f"Request failed: {failure.request.url}")
        self.logger.error(f"Error: {failure.value}")