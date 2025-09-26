# import scrapy
# from codeforces_scrapy.items import CodeforcesProblemItem

# class CodeforcesSpider(scrapy.Spider):
#     name = 'codeforces_spider'
#     allowed_domains = ['codeforces.com']
#     start_urls = ['https://codeforces.com/problemset']

#     def parse(self, response):
#         problem_links = response.css('a.problem_index::attr(href)').getall()
#         for link in problem_links:
#             yield response.follow(link, self.parse_problem)

#         next_page = response.css('a[title="Next page"]::attr(href)').get()
#         if next_page:
#             yield response.follow(next_page, self.parse)

#     def parse_problem(self, response):
#         item = CodeforcesProblemItem()
#         item['problem_id'] = response.css('div.problemindex::text').get().strip()
#         item['title'] = response.css('div.title h1::text').get().strip()
#         item['tags'] = response.css('div.tags a::text').getall()
#         item['difficulty'] = response.css('div.problem-difficulty::text').get().strip()
#         item['submission_stats'] = response.css('div.statistic span::text').getall()

#         yield item
# ...existing code...
import json
import scrapy

from codeforces_scrapy.items import CodeforcesProblem


class CodeforcesApiSpider(scrapy.Spider):
    name = "codeforces_spider"
    allowed_domains = ["codeforces.com"]
    start_urls = ["https://codeforces.com/api/problemset.problems"]

    def parse(self, response):
        data = json.loads(response.text)
        if data.get("status") != "OK":
            self.logger.error("API did not return OK status")
            return

        result = data.get("result", {})
        problems = result.get("problems", [])
        stats = result.get("problemStatistics", [])

        # build lookup for solvedCount by (contestId, index)
        stats_lookup = {}
        for s in stats:
            key = f"{s.get('contestId')}_{s.get('index')}"
            stats_lookup[key] = s.get("solvedCount", 0)

        for p in problems:
            contest_id = p.get("contestId")
            index = p.get("index")
            title = p.get("name")
            rating = p.get("rating")  # may be None
            tags = p.get("tags", [])

            key = f"{contest_id}_{index}"
            solved_count = stats_lookup.get(key, 0)

            item = CodeforcesProblem()
            item["contest_id"] = contest_id
            item["index"] = index
            item["problem_id"] = f"{contest_id}{index}"
            item["title"] = title
            item["tags"] = tags
            item["rating"] = rating
            item["solved_count"] = solved_count
            item["url"] = (
                f"https://codeforces.com/problemset/problem/{contest_id}/{index}"
                if contest_id is not None
                else f"https://codeforces.com/problemset/problem/{index}"
            )

            yield item
# ...existing code...