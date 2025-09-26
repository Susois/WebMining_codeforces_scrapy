def extract_problem_data(response):
    problems = []
    for problem in response.css('div.problem'):
        problem_data = {
            'id': problem.css('div.problem-id::text').get(),
            'title': problem.css('div.problem-title a::text').get(),
            'tags': problem.css('div.problem-tags a::text').getall(),
            'difficulty': problem.css('div.problem-difficulty::text').get(),
            'submissions': problem.css('div.problem-submissions::text').get(),
        }
        problems.append(problem_data)
    return problems

def clean_data(problem_data):
    cleaned_data = []
    for problem in problem_data:
        cleaned_problem = {
            'id': problem['id'].strip(),
            'title': problem['title'].strip(),
            'tags': [tag.strip() for tag in problem['tags']],
            'difficulty': problem['difficulty'].strip(),
            'submissions': int(problem['submissions'].strip().replace(',', '')),
        }
        cleaned_data.append(cleaned_problem)
    return cleaned_data

def save_to_mongodb(collection, data):
    if data:
        collection.insert_many(data)

def load_from_mongodb(collection):
    return list(collection.find())

def analyze_tags(problem_data):
    tag_distribution = {}
    for problem in problem_data:
        for tag in problem['tags']:
            tag_distribution[tag] = tag_distribution.get(tag, 0) + 1
    return tag_distribution

def analyze_difficulty(problem_data):
    difficulty_count = {}
    for problem in problem_data:
        difficulty = problem['difficulty']
        difficulty_count[difficulty] = difficulty_count.get(difficulty, 0) + 1
    return difficulty_count