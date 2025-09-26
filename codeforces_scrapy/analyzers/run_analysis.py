import os
import pymongo
import pandas as pd
from dotenv import load_dotenv

from content_analysis import (
    analyze_tag_distribution,
    analyze_difficulty_distribution,
    analyze_submission_statistics,
)
from structure_analysis import analyze_structure, visualize_structure


def load_data_from_mongo():
    load_dotenv()  # load biến môi trường từ .env

    uri = os.getenv("MONGODB_URI") or "mongodb://localhost:27017"
    db_name = os.getenv("MONGODb_DB", "codeforces")
    collection_name = os.getenv("MONGODB_COLLECTION", "problems")

    client = pymongo.MongoClient(uri)
    db = client[db_name]
    col = db[collection_name]
    return list(col.find({}))


if __name__ == "__main__":
    data = load_data_from_mongo()
    print(f"Loaded {len(data)} problems from MongoDB")

    # Tạo folder csv_analysis nếu chưa có
    output_dir = "csv_analysis"
    os.makedirs(output_dir, exist_ok=True)

    # === Content Analysis ===
    print("\n=== Content Analysis ===")

    tag_dist = analyze_tag_distribution(data)
    print("\nTop 10 tags:")
    print(tag_dist.head(10))
    tag_dist.to_csv(os.path.join(output_dir, "tag_distribution.csv"), index=False)

    diff_dist = analyze_difficulty_distribution(data)
    print("\nDifficulty distribution:")
    print(diff_dist.head(10))
    diff_dist.to_csv(os.path.join(output_dir, "difficulty_distribution.csv"), index=False)

    subm_stats = analyze_submission_statistics(data)
    print("\nSubmission stats (sample):")
    print(subm_stats.head(10))
    subm_stats.to_csv(os.path.join(output_dir, "submission_statistics.csv"), index=False)

    # === Structure Analysis ===
    print("\n=== Structure Analysis ===")
    structure = analyze_structure(data)
    visualize_structure(structure, limit=5)

    print(f"\n✅ Phân tích xong. Kết quả CSV đã lưu trong folder '{output_dir}'")
