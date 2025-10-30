# Codeforces Web Mining Project - Complete Guide

## 📋 Tổng quan Hệ thống

Hệ thống bao gồm:
1. **Scrapy Spider** - Crawl dữ liệu từ Codeforces API
2. **MongoDB** - Lưu trữ dữ liệu (3 collections: problems, users, submissions)
3. **Web Mining Analysis** - Phân tích theo 3 trụ cột
4. **Random Forest Model** - Dự đoán rating cho bài toán null
5. **React Dashboard** - Visualize kết quả

---

## 🚀 Bước 1: Setup Môi trường

### 1.1 Cài đặt Python dependencies

```bash
pip install requirements.txt
```

## 🕷️ Bước 2: Crawl Dữ liệu

### 2.1 Cấu trúc thư mục

```
codeforces_project/
├── codeforces_scrapy/
│   ├── __init__.py
│   ├── settings.py                    # File settings của bạn
│   ├── items.py                       # Enhanced items
│   ├── mongo_pipeline.py              # Enhanced MongoDB pipeline
│   └── spiders/
│       ├── __init__.py
│       └── codeforces_spider.py       # Enhanced spider
├── analysis/
│   └── web_mining_analysis.py         # Script phân tích         
├── ML_randomforest/
│   └── rating_predictor.py            # Random Forest model
├── dashboard/
│   └── dashboard.html                 # React dashboard
├── .env
└── requirements.txt
```

### 2.2 Chạy Spider

```bash
# Di chuyển vào thư mục project
cd codeforces_scrapy

# Chạy spider để crawl problems, users và submissions
scrapy crawl codeforces_enhanced

# Hoặc lưu ra file JSON (optional)
scrapy crawl codeforces_enhanced -o output.json
```

**Lưu ý:** 
- Spider sẽ crawl ~10,000 problems
- Top 500 users với rating cao nhất
- 100 submissions gần nhất của mỗi user
- Tổng thời gian: ~30-60 phút (do delay 2s giữa các request)

---

## 📊 Bước 3: Phân tích Web Mining

### 3.1 Chạy Content, Structure, Usage Mining

```python
# File: analysis/web_mining_analysis.py
from web_mining_analysis import CodeforcesWebMining

analyzer = CodeforcesWebMining()
report = analyzer.generate_comprehensive_report()

print("Analysis completed! Check MongoDB collection: analysis_reports")
```

### 3.2 Kết quả phân tích

Hệ thống sẽ phân tích theo 3 trụ cột:

#### **1. Content Mining:**
- Phân bố tags (math, dp, greedy, etc.)
- Phân tích độ khó (rating distribution)
- Clustering problems theo topics
- Phân tích title length

#### **2. Structure Mining:**
- Cấu trúc contests (số bài/contest)
- Mạng lưới co-occurrence của tags
- Phân tích difficulty progression
- Problem index distribution (A, B, C, ...)

#### **3. Usage Mining:**
- Ngôn ngữ lập trình phổ biến
- Verdict distribution (OK, WA, TLE...)
- Success rate theo language
- User activity patterns
- Time & memory performance

---

## 🤖 Bước 4: Random Forest - Dự đoán Rating

### 4.1 Chạy Model Training & Prediction

```python
# File: analysis/rating_predictor.py
from rating_predictor import CodeforcesRatingPredictor

predictor = CodeforcesRatingPredictor()
predictions = predictor.run_full_pipeline()

# Model sẽ:
# 1. Load dữ liệu từ MongoDB
# 2. Feature engineering (tags, solved_count, title_length...)
# 3. Train Random Forest (200 trees)
# 4. Evaluate (MAE, RMSE, R²)
# 5. Predict rating cho problems null
# 6. Update MongoDB với predicted_rating
# 7. Save model to file
```

### 4.2 Model Performance Expected

- **MAE (Mean Absolute Error):** ~100-150
- **RMSE:** ~150-200
- **R² Score:** ~0.85-0.90
- **Features:** ~50+ (tags + numerical features)

### 4.3 Load Model để dự đoán mới

```python
predictor = CodeforcesRatingPredictor()
predictor.load_model('codeforces_rating_model.pkl')

# Dự đoán cho bài mới
new_problem_features = {...}
predicted_rating = predictor.model.predict([new_problem_features])
```

---

## 📈 Bước 5: Dashboard Visualization

### 5.1 Setup Dashboard

Dashboard được build bằng React + Recharts. Có 2 cách chạy:

#### Option 1: Chạy trực tiếp HTML (Simple)

```html
<!-- File: dashboard/dashboard.html -->
<!DOCTYPE html>
<html>
<head>
    <script crossorigin src="https://unpkg.com/react@18/umd/react.production.min.js"></script>
    <script crossorigin src="https://unpkg.com/react-dom@18/umd/react-dom.production.min.js"></script>
    <script src="https://unpkg.com/@babel/standalone/babel.min.js"></script>
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://unpkg.com/recharts@2.5.0/dist/Recharts.js"></script>
</head>
<body>
    <div id="root"></div>
    <script type="text/babel">
        // Paste dashboard code here
    </script>
</body>
</html>
```

#### Option 2: React Project (Production)

```bash
# Tạo React app
npx create-react-app codeforces-dashboard
cd codeforces-dashboard

# Install dependencies
npm install recharts lucide-react

# Copy dashboard code vào src/App.js
# Run
npm start
```

### 5.2 Connect Dashboard với MongoDB

Tạo API Backend (Flask/FastAPI):

```python
# File: api/server.py
from flask import Flask, jsonify
from pymongo import MongoClient
import os

app = Flask(__name__)
client = MongoClient(os.getenv("MONGODB_URI"))
db = client["codeforces"]

@app.route('/api/problems')
def get_problems():
    problems = list(db.problems.find({}, {'_id': 0}).limit(1000))
    return jsonify(problems)

@app.route('/api/users')
def get_users():
    users = list(db.users.find({}, {'_id': 0}).limit(500))
    return jsonify(users)

@app.route('/api/submissions')
def get_submissions():
    submissions = list(db.submissions.find({}, {'_id': 0}).limit(5000))
    return jsonify(submissions)

@app.route('/api/analysis')
def get_analysis():
    report = db.analysis_reports.find_one({}, {'_id': 0}, sort=[('timestamp', -1)])
    return jsonify(report)

if __name__ == '__main__':
    app.run(port=5000, debug=True)
```

Run API:
```bash
pip install flask flask-cors
python api/server.py
```

Update Dashboard để fetch từ API:
```javascript
useEffect(() => {
    fetch('http://localhost:5000/api/problems')
        .then(res => res.json())
        .then(data => setData({...data, problems: data}));
}, []);
```

---

## 📊 Dashboard Features

Dashboard có 5 tabs:

### 1. **Overview**
- Tổng quan statistics
- Rating distribution chart
- Top languages bar chart
- Key metrics cards

### 2. **Content Mining**
- Tag distribution (Pie chart)
- Difficulty trend over time (Line chart)
- Tag co-occurrence network
- Problem clustering visualization

### 3. **Structure Mining**
- Contest size distribution
- Problem index analysis
- Difficulty progression patterns
- Tag relationship graphs

### 4. **Usage Mining**
- Verdict distribution (Pie chart)
- Language success rates
- User activity heatmap
- Performance metrics (time, memory)

### 5. **Predictions**
- Predicted vs Actual ratings scatter plot
- Model metrics (MAE, R², RMSE)
- Recent predictions table
- Confidence intervals

---

## 🔍 Query Examples từ MongoDB

### Tìm top 10 bài khó nhất

```javascript
db.problems.find({rating: {$ne: null}})
    .sort({rating: -1})
    .limit(10)
```

### Tìm bài toán có tag "dp" và rating > 2000

```javascript
db.problems.find({
    tags: "dp",
    rating: {$gt: 2000}
})
```

### Thống kê submissions theo language

```javascript
db.submissions.aggregate([
    {$group: {
        _id: "$programming_language",
        count: {$sum: 1},
        successRate: {
            $avg: {$cond: [{$eq: ["$verdict", "OK"]}, 1, 0]}
        }
    }},
    {$sort: {count: -1}}
])
```

### Tìm user hoạt động nhiều nhất

```javascript
db.submissions.aggregate([
    {$group: {
        _id: "$author_handle",
        submissions: {$sum: 1}
    }},
    {$sort: {submissions: -1}},
    {$limit: 10}
])
```

---

## 📝 Troubleshooting

### Lỗi kết nối MongoDB
```
pymongo.errors.ServerSelectionTimeoutError
```
**Fix:** Kiểm tra:
- Connection string đúng format
- Whitelist IP trong MongoDB Atlas
- Network firewall không block

### Spider không crawl được
```
Forbidden 403 / Too Many Requests 429
```
**Fix:**
- Tăng `DOWNLOAD_DELAY` trong settings.py
- Giảm `CONCURRENT_REQUESTS`
- Thêm random delay

### Model không accurate
**Fix:**
- Tăng số features (thêm tags mới)
- Tune hyperparameters (n_estimators, max_depth)
- Thu thập thêm dữ liệu training

---

## 🎯 Next Steps

1. **Optimize Spider:** Crawl parallel với Scrapy Cloud
2. **Real-time Updates:** Setup cron job để auto-update
3. **Advanced ML:** Thử XGBoost, Neural Networks
4. **API Production:** Deploy Flask API lên Heroku/Railway
5. **Dashboard Deploy:** Host React app trên Vercel/Netlify

---

## 📚 Resources

- **Codeforces API Docs:** https://codeforces.com/apiHelp
- **Scrapy Docs:** https://docs.scrapy.org/
- **MongoDB Atlas:** https://www.mongodb.com/docs/atlas/
- **Scikit-learn:** https://scikit-learn.org/
- **Recharts:** https://recharts.org/

--- 
**Good luck! 🚀**