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

# Sanitize function - cải tiến
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

# Alias cho tương thích
convert_objectid = sanitize_document

# Initialize Flask
app = Flask(__name__)
CORS(app)

# MongoDB connection
# MongoDB connection with increased timeouts
MONGO_URI = os.getenv("MONGODB_URI")
if not MONGO_URI:
    print("CẢNH BÁO: MONGODB_URI không được tìm thấy trong .env")
    MONGO_URI = "mongodb+srv://admin:Subaru1615@susoiswebminingcodeforc.ttmjjlf.mongodb.net/"

# Tăng timeout cho MongoDB connection
client = MongoClient(
    MONGO_URI,
    serverSelectionTimeoutMS=60000,  # 60 seconds
    socketTimeoutMS=120000,  # 120 seconds
    connectTimeoutMS=60000,  # 60 seconds
    maxPoolSize=50,  # Increase connection pool
    retryWrites=True
)
db = client["codeforces"]

print("✅ Đã kết nối với MongoDB!")

# ==================== NEW ENDPOINTS FOR DASHBOARD ====================

@app.route('/api/data', methods=['GET'])
def get_all_data():
    """
    Endpoint chính cho Dashboard
    Trả về: problems + users + submissions + analysis report
    """
    try:
        print("\n" + "="*60)
        print("📊 FETCHING DATA FOR DASHBOARD")
        print("="*60)
        
        # Fetch data from collections - TẤT CẢ problems và users, 100k submissions
        problems = list(db.problems.find({}, {'_id': 0}))  # ALL problems
        users = list(db.users.find({}, {'_id': 0}))  # ALL users
        submissions = list(db.submissions.find({}, {'_id': 0}).limit(1000000))  # 100k submissions
        
        print(f"✅ Problems: {len(problems)}")
        print(f"✅ Users: {len(users)}")
        print(f"✅ Submissions: {len(submissions)}")
        
        # Fetch latest analysis report
        analysis_report = db.analysis_reports.find_one(
            {},
            {'_id': 0},
            sort=[("timestamp", -1)]
        )
        
        if not analysis_report:
            print("⚠️  No analysis report found! Creating empty structure...")
            print("💡 Run 'python web_mining_analysis.py' to generate analysis")
            analysis_report = {
                'content_mining': {},
                'structure_mining': {},
                'usage_mining': {},
                'timestamp': None
            }
        else:
            print(f"✅ Analysis Report: {analysis_report.get('timestamp', 'unknown')}")
            print(f"   └─ Content Mining: {len(analysis_report.get('content_mining', {}))} metrics")
            print(f"   └─ Structure Mining: {len(analysis_report.get('structure_mining', {}))} metrics")
            print(f"   └─ Usage Mining: {len(analysis_report.get('usage_mining', {}))} metrics")
        
        # Sanitize all data
        response = {
            'problems': convert_objectid(problems),
            'users': convert_objectid(users),
            'submissions': convert_objectid(submissions),
            'analysis': convert_objectid(analysis_report),
            'status': 'success'
        }
        
        print("="*60)
        print("✅ Data package ready for dashboard")
        print("="*60 + "\n")
        
        return jsonify(response)
    
    except Exception as e:
        print(f"\n❌ ERROR in /api/data: {e}\n")
        return jsonify({
            'error': str(e),
            'status': 'error'
        }), 500


@app.route('/api/analysis', methods=['GET'])
def get_analysis_only():
    """
    Lấy chỉ analysis report
    Hữu ích cho refresh riêng phần analysis
    """
    try:
        print("\n📊 Fetching latest analysis report...")
        
        analysis_report = db.analysis_reports.find_one(
            {},
            {'_id': 0},
            sort=[("timestamp", -1)]
        )
        
        if not analysis_report:
            print("⚠️  No analysis report found in database!")
            print("💡 Run 'python web_mining_analysis.py' to generate analysis first\n")
            return jsonify({
                'error': 'No analysis report found',
                'message': 'Please run web_mining_analysis.py first to generate the report',
                'status': 'error',
                'analysis': {
                    'content_mining': {},
                    'structure_mining': {},
                    'usage_mining': {}
                }
            }), 404
        
        print(f"✅ Found analysis report from {analysis_report.get('timestamp', 'unknown')}")
        print(f"   └─ Content Mining: {len(analysis_report.get('content_mining', {}))} keys")
        print(f"   └─ Structure Mining: {len(analysis_report.get('structure_mining', {}))} keys")
        print(f"   └─ Usage Mining: {len(analysis_report.get('usage_mining', {}))} keys\n")
        
        return jsonify({
            'analysis': convert_objectid(analysis_report),
            'status': 'success'
        })
    
    except Exception as e:
        print(f"❌ Error in /api/analysis: {e}\n")
        return jsonify({
            'error': str(e),
            'status': 'error'
        }), 500


# ==================== ORIGINAL ENDPOINTS (Kept for compatibility) ====================

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
            default_limit = limit if limit else 10000
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
            "total_analysis_reports": db.analysis_reports.count_documents({})
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
        
        # Check if analysis report exists
        has_analysis = db.analysis_reports.count_documents({}) > 0
        latest_analysis = db.analysis_reports.find_one({}, {'timestamp': 1}, sort=[("timestamp", -1)])
        
        return jsonify({
            "status": "healthy",
            "database": "connected",
            "collections": {
                "problems": db.problems.count_documents({}),
                "users": db.users.count_documents({}),
                "submissions": db.submissions.count_documents({}),
                "analysis_reports": db.analysis_reports.count_documents({})
            },
            "analysis": {
                "available": has_analysis,
                "latest_timestamp": latest_analysis.get('timestamp') if latest_analysis else None
            }
        })
    except Exception as e:
        return jsonify({
            "status": "unhealthy",
            "error": str(e)
        }), 500


if __name__ == '__main__':
    print("\n" + "="*70)
    print("🚀 Flask API Server - Codeforces Analytics Dashboard")
    print("="*70)
    print(f"📊 Database Collections:")
    print(f"   ├─ Problems: {db.problems.count_documents({}):,}")
    print(f"   ├─ Users: {db.users.count_documents({}):,}")
    print(f"   ├─ Submissions: {db.submissions.count_documents({}):,}")
    print(f"   └─ Analysis Reports: {db.analysis_reports.count_documents({})}")
    
    # Check if analysis exists
    latest_analysis = db.analysis_reports.find_one({}, {'timestamp': 1}, sort=[("timestamp", -1)])
    if latest_analysis:
        print(f"\n✅ Latest Analysis: {latest_analysis.get('timestamp', 'Unknown')}")
    else:
        print(f"\n⚠️  No analysis report found!")
        print(f"💡 Run: python web_mining_analysis.py")
    
    print("="*70)
    print("🌐 Server running at: http://localhost:5000")
    print("="*70)
    print("📍 API Endpoints:")
    print("   🎯 DASHBOARD ENDPOINTS (Primary):")
    print("      GET /api/data              - Complete data package for dashboard")
    print("      GET /api/analysis          - Analysis report only")
    print("      GET /api/health            - Health check with full status")
    print("")
    print("   📊 DATA ENDPOINTS (Legacy/Direct Access):")
    print("      GET /api/problems          - All problems")
    print("      GET /api/users             - All users")
    print("      GET /api/submissions       - Submissions (default 10k)")
    print("      GET /api/submissions/stats - Aggregated submission stats")
    print("      GET /api/stats             - Quick stats overview")
    print("="*70 + "\n")
    
    app.run(port=5000, debug=True, host='0.0.0.0')