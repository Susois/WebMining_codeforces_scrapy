import pytest
from codeforces_scrapy.mongo_pipeline import MongoPipeline
from codeforces_scrapy.items import CodeforcesProblemItem

@pytest.fixture
def mongo_pipeline():
    pipeline = MongoPipeline()
    yield pipeline
    pipeline.close_spider(None)

def test_process_item(mongo_pipeline):
    item = CodeforcesProblemItem(
        problem_id='1234',
        title='Sample Problem',
        tags=['greedy', 'dp'],
        difficulty='3',
        submission_stats={'solved': 1000, 'total': 5000}
    )
    
    result = mongo_pipeline.process_item(item, None)
    
    assert result is item
    # Add additional assertions to verify that the item is stored correctly in MongoDB
    # For example, check if the item exists in the database with the expected values.