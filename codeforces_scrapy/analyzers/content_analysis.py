from collections import Counter
import pandas as pd

def analyze_tag_distribution(data):
    """
    Phân tích phân bố số lượng bài theo tag.
    """
    tags = [tag for problem in data for tag in problem.get('tags', [])]
    tag_counts = Counter(tags)
    return pd.DataFrame(tag_counts.items(), columns=['Tag', 'Count']).sort_values(by='Count', ascending=False)

def analyze_difficulty_distribution(data):
    """
    Phân tích phân bố độ khó (rating).
    """
    difficulties = [problem.get('rating') for problem in data if problem.get('rating') is not None]
    difficulty_counts = Counter(difficulties)
    return pd.DataFrame(difficulty_counts.items(), columns=['Rating', 'Count']).sort_values(by='Rating')

def analyze_submission_statistics(data):
    """
    Phân tích thống kê submissions và solved count.
    """
    submission_stats = {
        'Problem ID': [],
        'Submitted Count': [],
        'Solved Count': []
    }
    
    for problem in data:
        submission_stats['Problem ID'].append(problem.get('problem_id'))
        submission_stats['Submitted Count'].append(problem.get('submitted_count', 0))
        submission_stats['Solved Count'].append(problem.get('solved_count', 0))
    
    return pd.DataFrame(submission_stats)
