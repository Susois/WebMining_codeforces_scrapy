"""
Web Mining Analysis cho Codeforces Data
Phân tích theo 3 trụ cột:
1. Content Mining: Phân tích nội dung (tags, difficulty, titles)
2. Structure Mining: Phân tích cấu trúc (contest relationships, problem networks)
3. Usage Mining: Phân tích hành vi người dùng (submissions, languages, patterns)
"""

import pandas as pd
import numpy as np
from pymongo import MongoClient
from collections import Counter, defaultdict
import networkx as nx
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import os


def convert_numpy_types(obj):
    """Đệ quy chuyển đổi toàn bộ kiểu NumPy sang Python thuần."""
    if isinstance(obj, dict):
        return {k: convert_numpy_types(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_numpy_types(i) for i in obj]
    elif isinstance(obj, tuple):
        return tuple(convert_numpy_types(i) for i in obj)
    elif isinstance(obj, np.integer):
        return int(obj)
    elif isinstance(obj, np.floating):
        return float(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    else:
        return obj


def convert_keys_to_str(obj):
    """Đệ quy chuyển đổi tất cả key của dict sang string (fix lỗi float key)."""
    if isinstance(obj, dict):
        return {str(k): convert_keys_to_str(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_keys_to_str(v) for v in obj]
    else:
        return obj


class CodeforcesWebMining:
    
    def __init__(self, mongo_uri=None, db_name="codeforces"):
        """Khởi tạo kết nối MongoDB"""
        self.mongo_uri = mongo_uri or os.getenv("MONGODB_URI")
        self.db_name = db_name
        self.client = MongoClient(self.mongo_uri)
        self.db = self.client[self.db_name]
        
        # Load data
        self.problems_df = None
        self.users_df = None
        self.submissions_df = None
        
    def load_data(self):
        """Load dữ liệu từ MongoDB vào DataFrame"""
        print("Loading data from MongoDB...")
        
        # Load problems
        problems = list(self.db.problems.find({}))
        self.problems_df = pd.DataFrame(problems)
        print(f"Loaded {len(self.problems_df)} problems")
        
        # Load users
        users = list(self.db.users.find({}))
        self.users_df = pd.DataFrame(users)
        print(f"Loaded {len(self.users_df)} users")
        
        # Load submissions
        submissions = list(self.db.submissions.find({}))
        self.submissions_df = pd.DataFrame(submissions)
        print(f"Loaded {len(self.submissions_df)} submissions")
        
    # ==================== CONTENT MINING ====================
    
    def content_mining_analysis(self):
        """
        Content Mining: Phân tích nội dung bài toán
        - Tag distribution
        - Difficulty analysis
        - Topic clustering
        - Title analysis
        """
        print("\n" + "="*60)
        print("CONTENT MINING ANALYSIS")
        print("="*60)
        
        results = {}
        
        # 1. Tag Analysis
        print("\n1. Tag Distribution Analysis:")
        all_tags = []
        for tags in self.problems_df['tags']:
            if isinstance(tags, list):
                all_tags.extend(tags)
        
        tag_counts = Counter(all_tags)
        results['top_tags'] = tag_counts.most_common(20)
        print(f"   Total unique tags: {len(tag_counts)}")
        print(f"   Top 10 tags: {tag_counts.most_common(10)}")
        
        # 2. Difficulty Distribution
        print("\n2. Difficulty (Rating) Distribution:")
        rating_dist = self.problems_df['rating'].value_counts().sort_index()
        results['rating_distribution'] = rating_dist.to_dict()
        print(f"   Problems with rating: {self.problems_df['rating'].notna().sum()}")
        print(f"   Problems without rating: {self.problems_df['rating'].isna().sum()}")
        print(f"   Average rating: {self.problems_df['rating'].mean():.0f}")
        
        # 3. Topic Clustering (từ tags)
        print("\n3. Problem Clustering by Tags:")
        problems_with_tags = self.problems_df[self.problems_df['tags'].apply(lambda x: len(x) > 0 if isinstance(x, list) else False)]
        
        if len(problems_with_tags) > 10:
            # Tạo feature vector từ tags
            tag_vectors = []
            for tags in problems_with_tags['tags']:
                tag_str = ' '.join(tags)
                tag_vectors.append(tag_str)
            
            vectorizer = TfidfVectorizer(max_features=50)
            X = vectorizer.fit_transform(tag_vectors)
            
            # KMeans clustering
            n_clusters = min(10, len(problems_with_tags) // 10)
            if n_clusters > 1:
                kmeans = KMeans(n_clusters=n_clusters, random_state=42)
                problems_with_tags['cluster'] = kmeans.fit_predict(X)
                
                results['clusters'] = {}
                for i in range(n_clusters):
                    cluster_problems = problems_with_tags[problems_with_tags['cluster'] == i]
                    cluster_tags = []
                    for tags in cluster_problems['tags']:
                        cluster_tags.extend(tags)
                    results['clusters'][i] = Counter(cluster_tags).most_common(5)
                    print(f"   Cluster {i}: {len(cluster_problems)} problems, top tags: {results['clusters'][i]}")
        
        # 4. Title Analysis
        print("\n4. Title Length Analysis:")
        self.problems_df['title_length'] = self.problems_df['title'].str.len()
        results['avg_title_length'] = self.problems_df['title_length'].mean()
        print(f"   Average title length: {results['avg_title_length']:.1f} characters")
        
        return results
    
    # ==================== STRUCTURE MINING ====================
    
    def structure_mining_analysis(self):
        """
        Structure Mining: Phân tích cấu trúc
        - Contest structure
        - Problem relationships
        - Tag co-occurrence network
        - Difficulty progression
        """
        print("\n" + "="*60)
        print("STRUCTURE MINING ANALYSIS")
        print("="*60)
        
        results = {}
        
        # 1. Contest Structure
        print("\n1. Contest Structure Analysis:")
        contest_counts = self.problems_df['contest_id'].value_counts()
        results['total_contests'] = len(contest_counts)
        results['avg_problems_per_contest'] = contest_counts.mean()
        print(f"   Total contests: {results['total_contests']}")
        print(f"   Average problems per contest: {results['avg_problems_per_contest']:.1f}")
        
        # 2. Tag Co-occurrence Network
        print("\n2. Tag Co-occurrence Network:")
        tag_pairs = defaultdict(int)
        for tags in self.problems_df['tags']:
            if isinstance(tags, list) and len(tags) > 1:
                for i in range(len(tags)):
                    for j in range(i+1, len(tags)):
                        pair = tuple(sorted([tags[i], tags[j]]))
                        tag_pairs[pair] += 1
        
        results['top_tag_pairs'] = sorted(tag_pairs.items(), key=lambda x: x[1], reverse=True)[:20]
        print(f"   Total tag pairs: {len(tag_pairs)}")
        print(f"   Top 5 co-occurring tags: {results['top_tag_pairs'][:5]}")
        
        # 3. Difficulty Progression in Contests
        print("\n3. Difficulty Progression Analysis:")
        contest_difficulty = []
        for contest_id in self.problems_df['contest_id'].unique()[:100]:  # Sample
            contest_probs = self.problems_df[self.problems_df['contest_id'] == contest_id]
            contest_probs = contest_probs.dropna(subset=['rating']).sort_values('index')
            if len(contest_probs) > 2:
                ratings = contest_probs['rating'].tolist()
                # Check if increasing
                is_increasing = all(ratings[i] <= ratings[i+1] for i in range(len(ratings)-1))
                contest_difficulty.append(is_increasing)
        
        if contest_difficulty:
            results['progressive_contests_pct'] = sum(contest_difficulty) / len(contest_difficulty) * 100
            print(f"   Contests with progressive difficulty: {results['progressive_contests_pct']:.1f}%")
        
        # 4. Problem Index Network
        print("\n4. Problem Index Distribution:")
        index_counts = self.problems_df['index'].value_counts()
        results['problem_index_distribution'] = index_counts.to_dict()
        print(f"   Most common indices: {index_counts.head()}")
        
        return results
    
    # ==================== USAGE MINING ====================
    
    def usage_mining_analysis(self):
        """
        Usage Mining: Phân tích hành vi người dùng
        - Submission patterns
        - Language preferences
        - Success rates
        - Time analysis
        - User behavior patterns
        """
        print("\n" + "="*60)
        print("USAGE MINING ANALYSIS")
        print("="*60)
        
        if self.submissions_df is None or len(self.submissions_df) == 0:
            print("No submission data available")
            return {}
        
        results = {}
        
        # 1. Programming Language Distribution
        print("\n1. Programming Language Analysis:")
        lang_counts = self.submissions_df['programming_language'].value_counts()
        results['top_languages'] = lang_counts.head(10).to_dict()
        print(f"   Total languages used: {len(lang_counts)}")
        print(f"   Top 5 languages: {lang_counts.head()}")
        
        # 2. Verdict Distribution
        print("\n2. Verdict Distribution:")
        verdict_counts = self.submissions_df['verdict'].value_counts()
        results['verdict_distribution'] = verdict_counts.to_dict()
        total_submissions = len(self.submissions_df)
        accepted = verdict_counts.get('OK', 0)
        results['acceptance_rate'] = (accepted / total_submissions * 100) if total_submissions > 0 else 0
        print(f"   Total submissions: {total_submissions}")
        print(f"   Acceptance rate: {results['acceptance_rate']:.2f}%")
        print(f"   Top verdicts: {verdict_counts.head()}")
        
        # 3. User Activity Patterns
        print("\n3. User Activity Patterns:")
        user_submission_counts = self.submissions_df['author_handle'].value_counts()
        results['avg_submissions_per_user'] = user_submission_counts.mean()
        results['max_submissions_user'] = user_submission_counts.max()
        print(f"   Average submissions per user: {results['avg_submissions_per_user']:.1f}")
        print(f"   Most active user submissions: {results['max_submissions_user']}")
        
        # 4. Time Performance Analysis
        print("\n4. Time Performance Analysis:")
        results['avg_time_millis'] = self.submissions_df['time_consumed_millis'].mean()
        results['avg_memory_bytes'] = self.submissions_df['memory_consumed_bytes'].mean()
        print(f"   Average execution time: {results['avg_time_millis']:.0f} ms")
        print(f"   Average memory usage: {results['avg_memory_bytes']/1024/1024:.2f} MB")
        
        # 5. Language Success Rate
        print("\n5. Language Success Rate Analysis:")
        lang_success = {}
        for lang in lang_counts.head(10).index:
            lang_subs = self.submissions_df[self.submissions_df['programming_language'] == lang]
            success_rate = (lang_subs['verdict'] == 'OK').sum() / len(lang_subs) * 100
            lang_success[lang] = success_rate
        
        results['language_success_rates'] = lang_success
        print("   Success rates by language:")
        for lang, rate in sorted(lang_success.items(), key=lambda x: x[1], reverse=True)[:5]:
            print(f"      {lang}: {rate:.2f}%")
        
        # 6. Problem Popularity (từ submissions)
        print("\n6. Problem Popularity Analysis:")
        if 'contest_id' in self.submissions_df.columns and 'problem_index' in self.submissions_df.columns:
            self.submissions_df['problem_key'] = (
                self.submissions_df['contest_id'].astype(str) + 
                self.submissions_df['problem_index'].astype(str)
            )
            popular_problems = self.submissions_df['problem_key'].value_counts().head(10)
            results['most_attempted_problems'] = popular_problems.to_dict()
            print(f"   Most attempted problems: {popular_problems.head()}")
        
        return results
    
    # ==================== COMPREHENSIVE REPORT ====================
    
    def generate_comprehensive_report(self):
        """Tạo báo cáo tổng hợp từ 3 trụ cột"""
        print("\n" + "="*60)
        print("COMPREHENSIVE WEB MINING REPORT")
        print("="*60)
        
        self.load_data()
        
        content_results = self.content_mining_analysis()
        structure_results = self.structure_mining_analysis()
        usage_results = self.usage_mining_analysis()
        
        report = {
            'content_mining': content_results,
            'structure_mining': structure_results,
            'usage_mining': usage_results,
            'timestamp': pd.Timestamp.now().isoformat()
        }
        
        # Save to MongoDB

        # vi db khong nhan gia tri float hoac int nen phai chuyen ve str
        report = convert_numpy_types(report)
        report = convert_keys_to_str(report)
        self.db.analysis_reports.insert_one(report)


        print("\n✓ Report saved to MongoDB (analysis_reports collection)")
        
        return report

# if __name__ == "__main__":
#     # Example usage
#     analyzer = CodeforcesWebMining()
#     report = analyzer.generate_comprehensive_report() 

if __name__ == "__main__":
    analyzer = CodeforcesWebMining(
        mongo_uri="mongodb+srv://admin:Subaru1615@susoiswebminingcodeforc.ttmjjlf.mongodb.net/",
        db_name="codeforces"
    )
    report = analyzer.generate_comprehensive_report()
