import scrapy


class CodeforcesProblem(scrapy.Item):
    """Item cho bài toán Codeforces"""
    contest_id = scrapy.Field()
    index = scrapy.Field()
    problem_id = scrapy.Field()
    title = scrapy.Field()
    tags = scrapy.Field()
    rating = scrapy.Field()
    solved_count = scrapy.Field()
    url = scrapy.Field()
    type = scrapy.Field()
    points = scrapy.Field()
    contest_name = scrapy.Field()


class CodeforcesUser(scrapy.Item):
    """Item cho user profile"""
    handle = scrapy.Field()
    rating = scrapy.Field()
    max_rating = scrapy.Field()
    rank = scrapy.Field()
    max_rank = scrapy.Field()
    country = scrapy.Field()
    organization = scrapy.Field()
    contribution = scrapy.Field()
    friend_of_count = scrapy.Field()
    registration_time = scrapy.Field()


class CodeforcesSubmission(scrapy.Item):
    """Item cho submission"""
    submission_id = scrapy.Field()
    contest_id = scrapy.Field()
    problem_index = scrapy.Field()
    problem_name = scrapy.Field()
    programming_language = scrapy.Field()
    verdict = scrapy.Field()
    testset = scrapy.Field()
    passed_test_count = scrapy.Field()
    time_consumed_millis = scrapy.Field()
    memory_consumed_bytes = scrapy.Field()
    creation_time = scrapy.Field()
    author_handle = scrapy.Field()
    participant_type = scrapy.Field()