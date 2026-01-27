import os
import pandas as pd
import joblib
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier
from sklearn.pipeline import Pipeline
from sklearn.metrics import classification_report, accuracy_score

def train_model():
    print("Loading datasets...")
    
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    data_dir = os.path.join(base_dir, "data", "dataset")
    models_dir = os.path.join(base_dir, "data", "models")
    os.makedirs(models_dir, exist_ok=True)
    
    # Load available datasets
    dfs = []
    
    scholarly_path = os.path.join(data_dir, "scholarly_data.csv")
    if os.path.exists(scholarly_path):
        df1 = pd.read_csv(scholarly_path)
        dfs.append(df1)
        
    hc3_path = os.path.join(data_dir, "hc3_authentic_subset.csv")
    if os.path.exists(hc3_path):
        df2 = pd.read_csv(hc3_path)
        # Ensure consistency in columns
        if 'source' in df2.columns:
            df2 = df2.drop(columns=['source'])
        dfs.append(df2)
        
    if not dfs:
        print("No datasets found! Run the creation scripts first.")
        return

    full_df = pd.concat(dfs, ignore_index=True)
    print(f"Total samples: {len(full_df)}")
    
    # Preprocessing
    # Map labels to 0 (human) and 1 (ai)
    label_map = {'human': 0, 'ai': 1}
    full_df['label_id'] = full_df['label'].map(label_map)
    
    # Handle any missing values
    full_df = full_df.dropna(subset=['text', 'label_id'])
    
    X = full_df['text']
    y = full_df['label_id']
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    print("Training Random Forest model...")
    
    # Create a pipeline with TF-IDF and Random Forest
    pipeline = Pipeline([
        ('tfidf', TfidfVectorizer(stop_words='english', max_features=5000)),
        ('clf', RandomForestClassifier(n_estimators=100, random_state=42))
    ])
    
    pipeline.fit(X_train, y_train)
    
    # Evaluation
    y_pred = pipeline.predict(X_test)
    print("Model Performance:")
    print(classification_report(y_test, y_pred))
    
    # Save the model
    model_path = os.path.join(models_dir, "ai_detector_rf.joblib")
    joblib.dump(pipeline, model_path)
    print(f"Model saved to {model_path}")

if __name__ == "__main__":
    train_model()
