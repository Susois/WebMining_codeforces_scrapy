# 🕷️ WebMining Codeforces Scrapy

Dự án phân tích và dự đoán xếp hạng bài toán Codeforces sử dụng Web Scraping, Web Mining Analysis và Machine Learning (Random Forest).

---

## 📋 Mục lục

- [Giới thiệu](#-giới-thiệu)
- [Cấu trúc dự án](#-cấu-trúc-dự-án)
- [Cài đặt thủ công](#-cài-đặt-thủ-công)
- [Hướng dẫn sử dụng](#-hướng-dẫn-sử-dụng)
- [Mô tả chi tiết](#-mô-tả-chi-tiết)
- [Resources](#-resources)

---

## 🎯 Giới thiệu

Dự án này thực hiện phân tích toàn diện dữ liệu từ Codeforces theo **3 trụ cột Web Mining**:

### 1️⃣ **Content Mining** (Phân tích nội dung)
- Phân tích tags, độ khó (rating)
- Phân cụm bài toán (clustering)
- Phân tích tiêu đề và chủ đề

### 2️⃣ **Structure Mining** (Phân tích cấu trúc)
- Cấu trúc contest
- Mối quan hệ giữa các bài toán
- Tag co-occurrence network
- Độ khó tăng dần trong contest

### 3️⃣ **Usage Mining** (Phân tích hành vi người dùng)
- Submission patterns
- Ngôn ngữ lập trình phổ biến
- Tỷ lệ thành công (acceptance rate)
- Hiệu suất thời gian và bộ nhớ

### 🤖 **Machine Learning**
- Random Forest Regressor để dự đoán rating cho bài toán
- Feature engineering từ tags, solved_count, contest structure
- Model evaluation với MAE, RMSE, R² score

---

## 📁 Cấu trúc dự án

```
WEBMINING_CODEFORCES_SCRAPY/
│
├── analysis/                          # Phân tích Web Mining
│   └── web_mining_analysis.py         # 3 trụ cột: Content, Structure, Usage
│
├── api/                               # Flask REST API
│   └── server.py                      # Backend API endpoints
│
├── codeforces_scrapy/                 # Scrapy crawler
│   ├── spiders/
│   │   └── codeforces_spider.py       # Spider crawl Codeforces API
│   ├── items.py                       # Data models
│   ├── mongo_pipeline.py              # MongoDB pipeline
│   └── settings.py                    # Scrapy settings
│
├── codeforces-dashboard/              # React Dashboard
│   ├── src/
│   │   ├── App.js                     # Main dashboard
│   │   ├── services/
│   │   │   └── api.js                 # API client
│   │   └── App.css
│   ├── public/
│   └── package.json
│
├── ML_randomforest/                   # Machine Learning
│   ├── rating_predictor.py            # Random Forest model
│   └── codeforces_rating_model.pkl    # Trained model (generated)
│
├── .env                               # Environment variables
├── requirements.txt                   # Python dependencies
├── scrapy.cfg                         # Scrapy configuration
├── run.bat                            # run
└── README.md                          # File này
```
---

###  Chạy toàn bộ hệ thống để truy cập dashboard

```bash
# Chạy trực tiếp file run.bat   
run.bat

```
---

## 🔧 Cài đặt thủ công

### 1. Clone repository

```bash
git clone <repository-url>
cd WebMining_codeforces_scrapy
```

### 2. Thiết lập Backend (Python + Flask)

```bash
# Tạo virtual environment
python -m venv venv

# Kích hoạt virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Cài đặt dependencies
pip install -r requirements.txt
```

**File `requirements.txt`:**
```txt
scrapy>=2.11.0
pymongo>=4.6.0
python-dotenv>=1.0.0
pandas>=2.0.0
numpy>=1.24.0
scikit-learn>=1.3.0
joblib>=1.3.0
networkx>=3.0
flask>=3.0.0
flask-cors>=4.0.0
```

### 3. Thiết lập Frontend (React)

```bash
cd codeforces-dashboard

# Cài đặt dependencies
npm install

# Hoặc với yarn
yarn install
```

### 4. Cấu hình `.env`

(không cần, có sẵn trên git)

### 5. Chạy ứng dụng

**Terminal 1 - Backend:**
```bash
python api/server.py
```

**Terminal 2 - Frontend:**
```bash
cd codeforces-dashboard
npm start
```

---

## 🚀 Hướng dẫn sử dụng

### 1️⃣ Crawl dữ liệu (Optional - mất nhiều thời gian)

> ⚠️ **Lưu ý**: Bước này mất 2-3 giờ. Bạn có thể bỏ qua nếu đã có dữ liệu trong MongoDB.

```bash
cd codeforces_scrapy

# Chạy spider
scrapy crawl codeforces_enhanced

# Hoặc với settings tùy chỉnh
scrapy crawl codeforces_enhanced -s CONCURRENT_REQUESTS=1 -s DOWNLOAD_DELAY=2
```

**Dữ liệu được thu thập:**
- ✅ Problems: >10,000 bài toán
- ✅ Users: Top 2,000 users
- ✅ Submissions: ~950,000 submissions

### 2️⃣ Phân tích Web Mining

```bash
python analysis/web_mining_analysis.py
```

**Kết quả phân tích:**
- Content Mining: Tag distribution, difficulty analysis, clustering
- Structure Mining: Contest structure, tag co-occurrence
- Usage Mining: Submission patterns, language preferences, success rates

Kết quả được lưu vào MongoDB collection `analysis_reports`.

### 3️⃣ Huấn luyện mô hình Random Forest

```bash
python ML_randomforest/rating_predictor.py
```

**Quy trình:**
1. Load dữ liệu từ MongoDB
2. Feature engineering (tags, solved_count, title_length, etc.)
3. Train Random Forest với 200 trees
4. Evaluate model (MAE, RMSE, R²)
5. Predict rating cho bài toán chưa có rating
6. Lưu predictions vào MongoDB
7. Lưu trained model (.pkl file)

**Kết quả mong đợi:**
```
Test Set:
  MAE: ~150-200
  RMSE: ~200-250
  R²: 0.85-0.90
```

### 4️⃣ Khởi động Dashboard

**Thủ công:**
```bash
# Terminal 1 - Backend
python api/server.py

# Terminal 2 - Frontend
cd codeforces-dashboard
npm start
```

Truy cập: http://localhost:3000

---

## 📊 Mô tả chi tiết

### Web Mining Analysis (`web_mining_analysis.py`)

#### **1. Content Mining**
```python
def content_mining_analysis(self):
    # Tag distribution
    # Difficulty (rating) distribution
    # Problem clustering by tags (KMeans)
    # Title length analysis
```

**Insights:**
- Top tags: implementation, math, greedy, dp
- Rating distribution: 800-3500
- Clustering: 10 clusters by topic similarity

#### **2. Structure Mining**
```python
def structure_mining_analysis(self):
    # Contest structure analysis
    # Tag co-occurrence network
    # Difficulty progression in contests
    # Problem index distribution
```

**Insights:**
- Average problems per contest: 5-7
- Tag pairs: (dp, greedy), (graphs, trees)
- Progressive difficulty: 60-70% contests

#### **3. Usage Mining**
```python
def usage_mining_analysis(self):
    # Programming language distribution
    # Verdict distribution
    # User activity patterns
    # Time/memory performance
    # Language success rates
```

**Insights:**
- Top languages: GNU C++17, C++20, C++23
- Acceptance rate: ~30-40%
- Most active users: 500+ submissions

### Random Forest Model (`rating_predictor.py`)

#### **Features Engineering**
```python
Features = [
    'title_length',        # Độ dài tiêu đề
    'num_tags',           # Số lượng tags
    'index_position',     # Vị trí trong contest (A=1, B=2, ...)
    'solved_count',       # Số người giải được
    'contest_type',       # GYM hoặc REGULAR
    'tag_*'               # One-hot encoding 50+ tags
]
```

#### **Model Architecture**
```python
RandomForestRegressor(
    n_estimators=4999,      #  decision trees
    max_depth=20,          # Depth limit
    min_samples_split=5,
    min_samples_leaf=2,
    random_state=42
)
```

#### **Evaluation Metrics**
- **MAE** (Mean Absolute Error): Sai số trung bình
- **RMSE** (Root Mean Squared Error): Sai số bình phương
- **R² Score**: Hệ số xác định (0-1, càng cao càng tốt)

### Dashboard Features

#### **Overview Tab**
- Total statistics
- Rating distribution chart
- Top programming languages

#### **Content Mining Tab**
- Top problem tags (Pie chart)
- Tag distribution (Bar chart)
- Clustering results

#### **Structure Mining Tab**
- Contest structure metrics
- Tag co-occurrence network
- Difficulty progression

#### **Usage Mining Tab**
- Verdict distribution (Pie chart)
- Submission statistics
- Language success rates

#### **Predictions Tab**
- Predicted ratings for problems
- Model performance metrics
- Sample predictions table


---

## 📚 Resources

### Codeforces API Documentation
- API Docs: https://codeforces.com/apiHelp
- Rate Limits: 5 requests/second
- Methods:
  - `problemset.problems`: Lấy danh sách bài toán
  - `user.ratedList`: Lấy danh sách users
  - `user.status`: Lấy submissions của user

### Technologies Used

#### **Backend**
- **Scrapy**: Web scraping framework
- **MongoDB**: NoSQL database
- **Flask**: REST API framework
- **Flask-CORS**: Cross-origin requests

#### **Machine Learning**
- **scikit-learn**: Random Forest, preprocessing
- **pandas**: Data manipulation
- **numpy**: Numerical computing

#### **Frontend**
- **React**: UI framework
- **Recharts**: Data visualization
- **Lucide Icons**: Icon library
- **Axios**: HTTP client

#### **DevOps**
- **Docker**: Containerization
- **Docker Compose**: Multi-container orchestration

### Project Structure Explanation

```
analysis/          → Web Mining analysis scripts
api/               → Flask backend server
codeforces_scrapy/ → Scrapy crawler
  ├── spiders/     → Spider implementations
  ├── items.py     → Data models
  ├── pipelines.py → Data processing pipelines
  └── settings.py  → Crawler configuration
codeforces-dashboard/ → React frontend
ML_randomforest/   → Machine Learning models
```
---

## 📝 Notes

### Thời gian thực thi
- **Crawl dữ liệu**: 2-3 giờ (10K problems + 2K users + 1M submissions)
- **Web Mining Analysis**: 5-10 phút
- **Train Random Forest**: 2-5 phút
- **Dashboard load**: 10-20 giây

### Dung lượng
- MongoDB data: ~500MB
- Node modules: ~200MB
- Python packages: ~300MB
