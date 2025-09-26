def clean_problem_data(problem_data):
    # Function to clean and transform the scraped problem data
    cleaned_data = {}
    
    # Example cleaning steps
    cleaned_data['id'] = problem_data.get('id', '').strip()
    cleaned_data['title'] = problem_data.get('title', '').strip()
    cleaned_data['tags'] = [tag.strip() for tag in problem_data.get('tags', [])]
    cleaned_data['difficulty'] = problem_data.get('difficulty', None)
    cleaned_data['submissions'] = problem_data.get('submissions', 0)
    
    return cleaned_data

def transform_problem_data(raw_data):
    # Function to transform raw problem data into a structured format
    transformed_data = {
        'problem_id': raw_data['id'],
        'problem_title': raw_data['title'],
        'problem_tags': raw_data['tags'],
        'problem_difficulty': raw_data['difficulty'],
        'submission_count': raw_data['submissions']
    }
    
    return transformed_data

def process_data(raw_data):
    # Main function to process the scraped data
    cleaned_data = clean_problem_data(raw_data)
    transformed_data = transform_problem_data(cleaned_data)
    
    return transformed_data