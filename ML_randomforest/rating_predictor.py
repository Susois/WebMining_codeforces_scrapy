"""
Random Forest Model để dự đoán Rating cho các bài toán có rating = NULL
Features: tags, solved_count, contest_id, index, title_length
"""

import pandas as pd
import numpy as np
from pymongo import MongoClient
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import MultiLabelBinarizer, StandardScaler
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import joblib
import os


class CodeforcesRatingPredictor:
    
    def __init__(self, mongo_uri=None, db_name="codeforces"):
        """Khởi tạo predictor"""
        self.mongo_uri = mongo_uri or os.getenv("MONGODB_URI")
        self.db_name = db_name
        self.client = MongoClient(self.mongo_uri)
        self.db = self.client[self.db_name]
        
        self.model = None
        self.mlb = None
        self.scaler = None
        self.feature_names = []
        
    def load_and_prepare_data(self):
        """Load và chuẩn bị dữ liệu"""
        print("Loading problems from MongoDB...")
        problems = list(self.db.problems.find({}))
        df = pd.DataFrame(problems)
        
        print(f"Total problems: {len(df)}")
        print(f"Problems with rating: {df['rating'].notna().sum()}")
        print(f"Problems without rating: {df['rating'].isna().sum()}")
        
        return df
    
    def engineer_features(self, df):
        """Feature engineering"""
        print("\nEngineering features...")
        
        # 1. Title length
        df['title_length'] = df['title'].str.len()
        
        # 2. Number of tags
        df['num_tags'] = df['tags'].apply(lambda x: len(x) if isinstance(x, list) else 0)
        
        # 3. Contest type (từ contest_id)


        # Chuyển contest_id về kiểu số (và loại bỏ giá trị không hợp lệ)
        df['contest_id'] = pd.to_numeric(df['contest_id'], errors='coerce')

        # Nếu có giá trị NaN (do ép kiểu thất bại), có thể loại bỏ hoặc thay thế
        df = df.dropna(subset=['contest_id'])

        # Ép kiểu int nếu cần
        df['contest_id'] = df['contest_id'].astype(int)

        # Giờ mới tạo cột contest_type
        # df['contest_type'] = df['contest_id'].apply(lambda x: 'GYM' if x >= 100000 else 'REGULAR')

        df['contest_type'] = df['contest_id'].apply(lambda x: 'GYM' if x >= 100000 else 'REGULAR')
        
        # 4. Index position (A=1, B=2, ...)
        df['index_position'] = df['index'].apply(
            lambda x: ord(x[0]) - ord('A') + 1 if isinstance(x, str) and len(x) > 0 else 0
        )
        
        # 5. One-hot encode tags
        print("Encoding tags...")
        valid_tags = df[df['tags'].apply(lambda x: isinstance(x, list) and len(x) > 0)]
        self.mlb = MultiLabelBinarizer()
        tag_encoded = self.mlb.fit_transform(valid_tags['tags'])
        tag_df = pd.DataFrame(tag_encoded, columns=self.mlb.classes_, index=valid_tags.index)
        df = df.join(tag_df)
        
        # Fill NaN trong tag columns với 0
        for col in self.mlb.classes_:
            if col in df.columns:
                df[col] = df[col].fillna(0)
        
        print(f"Total features after encoding: {len(self.mlb.classes_)} tags")
        
        return df
    
    def train_model(self, df):
        """Train Random Forest model"""
        print("\nTraining Random Forest model...")
        
        # Separate problems with và without rating
        df_with_rating = df[df['rating'].notna()].copy()
        df_without_rating = df[df['rating'].isna()].copy()
        
        print(f"Training set size: {len(df_with_rating)}")
        print(f"Prediction set size: {len(df_without_rating)}")
        
        # Features
        feature_cols = ['title_length', 'num_tags', 'index_position', 'solved_count']
        feature_cols.extend(self.mlb.classes_)  # Add tag features
        
        # Ensure all columns exist
        for col in feature_cols:
            if col not in df_with_rating.columns:
                df_with_rating[col] = 0
            if col not in df_without_rating.columns:
                df_without_rating[col] = 0
        
        X = df_with_rating[feature_cols].fillna(0)
        y = df_with_rating['rating']
        
        # Train/test split
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )
        
        # Scale features
        self.scaler = StandardScaler()
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        # Train Random Forest
        self.model = RandomForestRegressor(
            n_estimators=200,
            max_depth=20,
            min_samples_split=5,
            min_samples_leaf=2,
            random_state=42,
            n_jobs=-1,
            verbose=1
        )
        
        self.model.fit(X_train_scaled, y_train)
        self.feature_names = feature_cols
        
        # Evaluate
        print("\n" + "="*60)
        print("MODEL EVALUATION")
        print("="*60)
        
        y_pred_train = self.model.predict(X_train_scaled)
        y_pred_test = self.model.predict(X_test_scaled)
        
        print(f"\nTraining Set:")
        print(f"  MAE: {mean_absolute_error(y_train, y_pred_train):.2f}")
        print(f"  RMSE: {np.sqrt(mean_squared_error(y_train, y_pred_train)):.2f}")
        print(f"  R²: {r2_score(y_train, y_pred_train):.4f}")
        
        print(f"\nTest Set:")
        print(f"  MAE: {mean_absolute_error(y_test, y_pred_test):.2f}")
        print(f"  RMSE: {np.sqrt(mean_squared_error(y_test, y_pred_test)):.2f}")
        print(f"  R²: {r2_score(y_test, y_pred_test):.4f}")
        
        # Cross-validation
        print("\nCross-Validation (5-fold):")
        cv_scores = cross_val_score(
            self.model, X_train_scaled, y_train, 
            cv=5, scoring='neg_mean_absolute_error', n_jobs=-1
        )
        print(f"  CV MAE: {-cv_scores.mean():.2f} (+/- {cv_scores.std() * 2:.2f})")
        
        # Feature importance
        print("\nTop 20 Most Important Features:")
        feature_importance = pd.DataFrame({
            'feature': feature_cols,
            'importance': self.model.feature_importances_
        }).sort_values('importance', ascending=False)
        
        for idx, row in feature_importance.head(20).iterrows():
            print(f"  {row['feature']}: {row['importance']:.4f}")
        
        return df_without_rating, feature_cols
    
    def predict_missing_ratings(self, df_without_rating, feature_cols):
        """Dự đoán rating cho các bài chưa có rating"""
        print("\n" + "="*60)
        print("PREDICTING MISSING RATINGS")
        print("="*60)
        
        if len(df_without_rating) == 0:
            print("No problems without rating to predict!")
            return
        
        X_predict = df_without_rating[feature_cols].fillna(0)
        X_predict_scaled = self.scaler.transform(X_predict)
        
        predictions = self.model.predict(X_predict_scaled)
        
        # Round to nearest 100 (Codeforces ratings thường là bội của 100)
        predictions_rounded = (np.round(predictions / 100) * 100).astype(int)
        
        # Clip to valid range [800, 3500]
        predictions_rounded = np.clip(predictions_rounded, 800, 3500)
        
        df_without_rating['predicted_rating'] = predictions_rounded
        
        print(f"\nPredicted ratings for {len(df_without_rating)} problems")
        print(f"Rating distribution:")
        print(df_without_rating['predicted_rating'].value_counts().sort_index())
        
        # Update MongoDB
        print("\nUpdating MongoDB with predicted ratings...")
        updated_count = 0
        for idx, row in df_without_rating.iterrows():
            result = self.db.problems.update_one(
                {'contest_id': row['contest_id'], 'index': row['index']},
                {'$set': {'predicted_rating': int(row['predicted_rating'])}}
            )
            if result.modified_count > 0:
                updated_count += 1
        
        print(f"✓ Updated {updated_count} problems in MongoDB")
        
        return df_without_rating[['problem_id', 'title', 'tags', 'predicted_rating']]
    
    def save_model(self, filepath='codeforces_rating_model.pkl'):
        """Lưu model"""
        model_data = {
            'model': self.model,
            'mlb': self.mlb,
            'scaler': self.scaler,
            'feature_names': self.feature_names
        }
        joblib.dump(model_data, filepath)
        print(f"\n✓ Model saved to {filepath}")
    
    def load_model(self, filepath='codeforces_rating_model.pkl'):
        """Load model"""
        model_data = joblib.load(filepath)
        self.model = model_data['model']
        self.mlb = model_data['mlb']
        self.scaler = model_data['scaler']
        self.feature_names = model_data['feature_names']
        print(f"✓ Model loaded from {filepath}")
    
    def run_full_pipeline(self):
        """Chạy toàn bộ pipeline"""
        print("\n" + "="*60)
        print("CODEFORCES RATING PREDICTION PIPELINE")
        print("="*60)
        
        # 1. Load data
        df = self.load_and_prepare_data()
        
        # 2. Engineer features
        df = self.engineer_features(df)
        
        # 3. Train model
        df_without_rating, feature_cols = self.train_model(df)
        
        # 4. Predict missing ratings
        predictions = self.predict_missing_ratings(df_without_rating, feature_cols)
        
        # 5. Save model
        self.save_model()
        
        print("\n" + "="*60)
        print("PIPELINE COMPLETED SUCCESSFULLY!")
        print("="*60)
        
        return predictions


if __name__ == "__main__":
    # Run prediction pipeline
    predictor = CodeforcesRatingPredictor(
        mongo_uri="mongodb+srv://admin:Subaru1615@susoiswebminingcodeforc.ttmjjlf.mongodb.net/",
        db_name="codeforces"
    )
    predictions = predictor.run_full_pipeline()
    
    # Display sample predictions
    print("\nSample Predictions:")
    print(predictions.head(10))
