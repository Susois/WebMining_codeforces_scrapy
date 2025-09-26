import matplotlib.pyplot as plt
import networkx as nx
import os

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


def visualize_structure(structure, limit=5, output_dir=None):
    """
    In ra cấu trúc (giới hạn số lượng để dễ xem) + trực quan hóa bằng đồ thị.
    Nếu có output_dir thì lưu hình ảnh ra file PNG.
    """
    print(f"=== Contests (hiển thị {limit}) ===")
    for i, (contest_id, contest) in enumerate(structure['contests'].items()):
        if i >= limit: break
        print(f"  Contest ID: {contest_id}, Problems: {contest['problems'][:5]} ...")

    print(f"\n=== Problems (hiển thị {limit}) ===")
    for i, (problem_id, problem) in enumerate(structure['problems'].items()):
        if i >= limit: break
        print(f"  Problem ID: {problem_id}, Title: {problem['title']}, Tags: {problem['tags']}")

    print(f"\n=== Tags (hiển thị {limit}) ===")
    for i, (tag, tag_info) in enumerate(structure['tags'].items()):
        if i >= limit: break
        print(f"  Tag: {tag}, Problems: {tag_info['problems'][:5]} ...")

    # --- Vẽ Graph bằng NetworkX ---
    G = nx.Graph()

    contests = list(structure['contests'].items())[:limit]
    for contest_id, contest in contests:
        G.add_node(f"Contest {contest_id}", type="contest")
        for pid in contest['problems'][:limit]:
            G.add_node(f"Problem {pid}", type="problem")
            G.add_edge(f"Contest {contest_id}", f"Problem {pid}")
            for tag in structure['problems'][pid]['tags']:
                G.add_node(tag, type="tag")
                G.add_edge(f"Problem {pid}", tag)

    pos = nx.spring_layout(G, seed=42)
    node_colors = []
    for node, data in G.nodes(data=True):
        if data["type"] == "contest":
            node_colors.append("red")
        elif data["type"] == "problem":
            node_colors.append("blue")
        else:
            node_colors.append("green")

    plt.figure(figsize=(10, 8))
    nx.draw(G, pos, with_labels=True, node_size=800, font_size=8, node_color=node_colors)
    plt.title("Quan hệ Contest ↔ Problems ↔ Tags (giới hạn)")

    # Lưu ảnh nếu có output_dir
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
        out_path = os.path.join(output_dir, "structure_graph.png")
        plt.savefig(out_path, dpi=300, bbox_inches="tight")
        print(f"📷 Đã lưu hình ảnh graph tại: {out_path}")

    plt.show()