import pytest
from scrapy.http import Request
from codeforces_scrapy.spiders.codeforces_spider import CodeforcesSpider

@pytest.fixture
def spider():
    return CodeforcesSpider()

def test_start_requests(spider):
    requests = list(spider.start_requests())
    assert len(requests) > 0
    assert isinstance(requests[0], Request)
    assert requests[0].url == 'https://codeforces.com/problemset'

def test_parse(spider):
    response = type('Response', (object,), {'css': lambda self, x: ['test_problem'], 'xpath': lambda self, x: ['test_problem']})
    items = list(spider.parse(response))
    assert len(items) > 0
    assert 'test_problem' in items[0]['title']

def test_item_structure():
    item = {
        'problem_id': '123A',
        'title': 'Test Problem',
        'tags': ['greedy', 'implementation'],
        'difficulty': 1200,
        'submissions': 1000
    }
    assert isinstance(item['problem_id'], str)
    assert isinstance(item['title'], str)
    assert isinstance(item['tags'], list)
    assert isinstance(item['difficulty'], int)
    assert isinstance(item['submissions'], int)