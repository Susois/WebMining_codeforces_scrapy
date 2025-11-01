import os
import json
from flask import Flask, jsonify, request
from flask_cors import CORS
from pymongo import MongoClient, DESCENDING
from bson import ObjectId
from dotenv import load_dotenv

# Load environment variables
dotenv_path = os.path.join(os.path.dirname(__file__), '..', '.env')
load_dotenv(dotenv_path)

# Sanitize function
def sanitize_document(doc):
    """Đệ quy chuyển đổi ObjectId và các kiểu không-JSON thành string."""
    if isinstance(doc, dict):
        new_doc = {}
        for k, v in doc.items():
            if isinstance(k, (int, float)):
                k = str(k)
            if isinstance(v, ObjectId):
                new_doc[k] = str(v)
            elif isinstance(v, dict):
                new_doc[k] = sanitize_document(v)
            elif isinstance(v, list):
                new_doc[k] = [sanitize_document(item) for item in v]
            else:
                new_doc[k] = v
        return new_doc
    elif isinstance(doc, list):
        return [sanitize_document(item) for item in doc]
    elif isinstance(doc, ObjectId):
        return str(doc)
    return doc

# Initialize Flask
app = Flask(__name__)
CORS(app)

# MongoDB connection
MONGO_URI = os.getenv("MONGODB_URI")
if not MONGO_URI:
    print("LỖI: MONGODB_URI không được tìm thấy. Hãy kiểm tra file .env của bạn.")
    MONGO_URI = "mongodb+srv://admin:Subaru1615@susoiswebminingcodeforc.ttmjjlf.mongodb.net/"

client = MongoClient(MONGO_URI)
db = client["codeforces"]

print("Đã kết nối với MongoDB!")

# ==================== API ENDPOINTS ====================

@app.route('/api/problems')
def get_problems():
    """
    Lấy tất cả problems (không limit)
    Optional query params:
    - limit: số lượng records (default: all)
    - skip: bỏ qua n records đầu
    """
    try:
        limit = request.args.get('limit', type=int)
        skip = request.args.get('skip', default=0, type=int)
        
        query = {}
        cursor = db.problems.find(query, {'_id': 0}).skip(skip)
        
        if limit:
            cursor = cursor.limit(limit)
        
        problems = list(cursor)
        
        print(f"✅ Returned {len(problems)} problems (skip={skip}, limit={limit or 'all'})")
        return jsonify(sanitize_document(problems))
    except Exception as e:
        print(f"❌ Error in /api/problems: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/users')
def get_users():
    """Lấy tất cả users"""
    try:
        limit = request.args.get('limit', type=int)
        skip = request.args.get('skip', default=0, type=int)
        
        cursor = db.users.find({}, {'_id': 0}).skip(skip)
        
        if limit:
            cursor = cursor.limit(limit)
        
        users = list(cursor)
        
        print(f"✅ Returned {len(users)} users")
        return jsonify(sanitize_document(users))
    except Exception as e:
        print(f"❌ Error in /api/users: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/submissions')
def get_submissions():
    """
    Lấy submissions với pagination
    Query params:
    - limit: số lượng records (default: 10000 để tránh quá tải)
    - skip: bỏ qua n records
    - all: true để lấy tất cả (CẢNH BÁO: chậm với dataset lớn)
    """
    try:
        get_all = request.args.get('all', 'false').lower() == 'true'
        limit = request.args.get('limit', type=int)
        skip = request.args.get('skip', default=0, type=int)
        
        cursor = db.submissions.find({}, {'_id': 0}).sort("creation_time", DESCENDING).skip(skip)
        
        if get_all:
            # Lấy TẤT CẢ - có thể chậm!
            print("⚠️ WARNING: Fetching ALL submissions (this may take time)...")
            submissions = list(cursor)
        else:
            # Mặc định lấy 10000 để balance giữa performance và data
            default_limit = limit if limit else 50000
            submissions = list(cursor.limit(default_limit))
        
        print(f"✅ Returned {len(submissions)} submissions (skip={skip}, limit={limit or 'default'})")
        return jsonify(sanitize_document(submissions))
    except Exception as e:
        print(f"❌ Error in /api/submissions: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/submissions/stats')
def get_submission_stats():
    """
    Lấy statistics về submissions (nhanh hơn fetch all)
    Trả về aggregated data thay vì raw submissions
    """
    try:
        # Total count
        total = db.submissions.count_documents({})
        
        # Verdict distribution
        verdict_pipeline = [
            {"$group": {"_id": "$verdict", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}}
        ]
        verdicts = list(db.submissions.aggregate(verdict_pipeline))
        verdict_dist = {v["_id"]: v["count"] for v in verdicts}
        
        # Language distribution
        lang_pipeline = [
            {"$group": {"_id": "$programming_language", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}},
            {"$limit": 20}
        ]
        langs = list(db.submissions.aggregate(lang_pipeline))
        lang_dist = {l["_id"]: l["count"] for l in langs}
        
        # Average time and memory
        avg_pipeline = [
            {"$group": {
                "_id": None,
                "avg_time": {"$avg": "$time_consumed_millis"},
                "avg_memory": {"$avg": "$memory_consumed_bytes"}
            }}
        ]
        avg_result = list(db.submissions.aggregate(avg_pipeline))
        avg_stats = avg_result[0] if avg_result else {}
        
        stats = {
            "total_submissions": total,
            "verdict_distribution": verdict_dist,
            "language_distribution": lang_dist,
            "avg_time_millis": avg_stats.get("avg_time"),
            "avg_memory_bytes": avg_stats.get("avg_memory")
        }
        
        print(f"✅ Returned submission stats (total: {total})")
        return jsonify(sanitize_document(stats))
    except Exception as e:
        print(f"❌ Error in /api/submissions/stats: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/analysis')
def get_analysis():
    """Lấy báo cáo phân tích MỚI NHẤT"""
    try:
        report = db.analysis_reports.find_one({}, {'_id': 0}, sort=[('timestamp', -1)])
        
        if not report:
            return jsonify({
                "content_mining": {},
                "structure_mining": {},
                "usage_mining": {}
            })
        
        print("✅ Returned latest analysis report")
        return jsonify(sanitize_document(report))
    except Exception as e:
        print(f"❌ Error in /api/analysis: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/stats')
def get_stats():
    """
    Endpoint mới: Lấy tổng quan statistics
    Nhanh hơn nhiều so với fetch all data
    """
    try:
        stats = {
            "total_problems": db.problems.count_documents({}),
            "total_users": db.users.count_documents({}),
            "total_submissions": db.submissions.count_documents({}),
            "problems_with_rating": db.problems.count_documents({"rating": {"$ne": None}}),
            "problems_without_rating": db.problems.count_documents({"rating": None}),
        }
        
        # Average rating
        avg_rating_result = list(db.problems.aggregate([
            {"$match": {"rating": {"$ne": None}}},
            {"$group": {"_id": None, "avg_rating": {"$avg": "$rating"}}}
        ]))
        
        if avg_rating_result:
            stats["avg_rating"] = avg_rating_result[0]["avg_rating"]
        
        print(f"✅ Returned stats: {stats}")
        return jsonify(stats)
    except Exception as e:
        print(f"❌ Error in /api/stats: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/health')
def health_check():
    """Health check endpoint"""
    try:
        # Ping MongoDB
        client.admin.command('ping')
        return jsonify({
            "status": "healthy",
            "database": "connected",
            "collections": {
                "problems": db.problems.count_documents({}),
                "users": db.users.count_documents({}),
                "submissions": db.submissions.count_documents({})
            }
        })
    except Exception as e:
        return jsonify({
            "status": "unhealthy",
            "error": str(e)
        }), 500


if __name__ == '__main__':
    print("\n" + "="*60)
    print("Flask API Server - Codeforces Analytics")
    print("="*60)
    print(f"Problems: {db.problems.count_documents({})}")
    print(f"Users: {db.users.count_documents({})}")
    print(f"Submissions: {db.submissions.count_documents({})}")
    print("="*60)
    print("Flask server đang chạy tại http://localhost:5000")
    print("Endpoints:")
    print("  - GET /api/problems")
    print("  - GET /api/users")
    print("  - GET /api/submissions?limit=10000")
    print("  - GET /api/submissions?all=true  (lấy tất cả)")
    print("  - GET /api/submissions/stats  (nhanh)")
    print("  - GET /api/analysis")
    print("  - GET /api/stats")
    print("  - GET /api/health")
    print("="*60 + "\n")
    
    app.run(port=5000, debug=True)