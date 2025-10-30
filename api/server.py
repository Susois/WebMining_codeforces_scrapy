# # File: api/server.py
# from flask import Flask, jsonify
# from pymongo import MongoClient
# import os

# app = Flask(__name__)
# client = MongoClient(os.getenv("MONGODB_URI"))
# db = client["codeforces"]

# @app.route('/api/problems')
# def get_problems():
#     problems = list(db.problems.find({}, {'_id': 0}).limit(1000))
#     return jsonify(problems)

# @app.route('/api/users')
# def get_users():
#     users = list(db.users.find({}, {'_id': 0}).limit(500))
#     return jsonify(users)

# @app.route('/api/submissions')
# def get_submissions():
#     submissions = list(db.submissions.find({}, {'_id': 0}).limit(5000))
#     return jsonify(submissions)

# @app.route('/api/analysis')
# def get_analysis():
#     report = db.analysis_reports.find_one({}, {'_id': 0}, sort=[('timestamp', -1)])
#     return jsonify(report)

# if __name__ == '__main__':
#     app.run(port=5000, debug=True)
import os
import json
from flask import Flask, jsonify
from flask_cors import CORS  # Import CORS
from pymongo import MongoClient, DESCENDING
from bson import ObjectId
from dotenv import load_dotenv  # Import dotenv

# --- Nạp biến môi trường (MONGODB_URI) từ file .env ---
# Điều này giả định file .env của bạn nằm ở thư mục gốc (bên ngoài thư mục api)
dotenv_path = os.path.join(os.path.dirname(__file__), '..', '.env')
load_dotenv(dotenv_path)

# --- Hàm dọn dẹp dữ liệu ---
# (Lấy từ file export_for_react.py của bạn)
def sanitize_document(doc):
    """Đệ quy chuyển đổi ObjectId và các kiểu không-JSON thành string."""
    if isinstance(doc, dict):
        new_doc = {}
        for k, v in doc.items():
            if isinstance(k, (int, float)): # Chuyển key không phải string
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

# --- Khởi tạo Flask App ---
app = Flask(__name__)
# Kích hoạt CORS cho toàn bộ app
CORS(app) 

# --- Kết nối MongoDB ---
MONGO_URI = os.getenv("MONGODB_URI")
if not MONGO_URI:
    print("LỖI: MONGODB_URI không được tìm thấy. Hãy kiểm tra file .env của bạn.")
    # Sử dụng chuỗi kết nối cũ của bạn làm dự phòng (không khuyến khích)
    MONGO_URI = "mongodb+srv://admin:Subaru1615@susoiswebminingcodeforc.ttmjjlf.mongodb.net/"

client = MongoClient(MONGO_URI)
db = client["codeforces"]

print("Đã kết nối với MongoDB!")

# --- Các API Endpoints ---

@app.route('/api/problems')
def get_problems():
    problems = list(db.problems.find({}, {'_id': 0}).limit(2000))
    return jsonify(sanitize_document(problems))

@app.route('/api/users')
def get_users():
    users = list(db.users.find({}, {'_id': 0}))
    return jsonify(sanitize_document(users))

@app.route('/api/submissions')
def get_submissions():
    # Sắp xếp để lấy 5000 submissions mới nhất
    submissions = list(db.submissions.find({}, {'_id': 0}).sort("creation_time", DESCENDING).limit(5000))
    return jsonify(sanitize_document(submissions))

@app.route('/api/analysis')
def get_analysis():
    # Lấy báo cáo phân tích MỚI NHẤT
    report = db.analysis_reports.find_one({}, {'_id': 0}, sort=[('timestamp', -1)])
    if not report:
        return jsonify({
            "content_mining": {},
            "structure_mining": {},
            "usage_mining": {}
        })
    return jsonify(sanitize_document(report))

if __name__ == '__main__':
    print("Flask server đang chạy tại http://localhost:5000")
    app.run(port=5000, debug=True)
