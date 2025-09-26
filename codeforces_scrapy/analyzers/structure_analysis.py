def analyze_structure(data):
    """
    Xây dựng cấu trúc quan hệ Contest -> Problems -> Tags.
    """
    structure = {
        'contests': {},
        'problems': {},
        'tags': {}
    }

    for item in data:
        problem_id = item.get('problem_id')
        title = item.get('title')
        tags = item.get('tags', [])
        contest_id = item.get('contest_id')

        # Thêm problem
        structure['problems'][problem_id] = {
            'title': title,
            'tags': tags,
            'contest_id': contest_id
        }

        # Thêm contest
        if contest_id not in structure['contests']:
            structure['contests'][contest_id] = {
                'problems': []
            }
        structure['contests'][contest_id]['problems'].append(problem_id)

        # Thêm tags
        for tag in tags:
            if tag not in structure['tags']:
                structure['tags'][tag] = {
                    'problems': []
                }
            structure['tags'][tag]['problems'].append(problem_id)

    return structure


def visualize_structure(structure, limit=5):
    """
    In ra cấu trúc (giới hạn số lượng để dễ xem).
    """
    print("=== Contests (hiển thị {limit}) ===")
    for i, (contest_id, contest) in enumerate(structure['contests'].items()):
        if i >= limit: break
        print(f"  Contest ID: {contest_id}, Problems: {contest['problems'][:5]} ...")

    print("\n=== Problems (hiển thị {limit}) ===")
    for i, (problem_id, problem) in enumerate(structure['problems'].items()):
        if i >= limit: break
        print(f"  Problem ID: {problem_id}, Title: {problem['title']}, Tags: {problem['tags']}")

    print("\n=== Tags (hiển thị {limit}) ===")
    for i, (tag, tag_info) in enumerate(structure['tags'].items()):
        if i >= limit: break
        print(f"  Tag: {tag}, Problems: {tag_info['problems'][:5]} ...")
