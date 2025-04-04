import pandas as pd
import plotly.express as px
import re
import nltk
import json
from nltk.corpus import stopwords
from transformers import pipeline
import joblib
import os

import sys
sys.stdout.reconfigure(encoding='utf-8')

nltk.download('stopwords')
STOPWORDS = set(stopwords.words('english'))

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "svm_sentiment_model.pkl")
LR_MODEL_PATH = os.path.join(BASE_DIR, "lr_sentiment_model.pkl")
VECTORIZER_PATH = os.path.join(BASE_DIR, "tfidf_vectorizer.pkl")

# ---------------------- Load Models ----------------------
try:
    svm_model = joblib.load(MODEL_PATH)
    lr_model = joblib.load(LR_MODEL_PATH)
    vectorizer = joblib.load(VECTORIZER_PATH)
    print("✅ SVM and Logistic Regression models loaded successfully.")
except Exception as e:
    print(f"❌ Error loading models: {e}")
    svm_model = None
    lr_model = None
    vectorizer = None

try:
    bert_classifier = pipeline("text-classification", model="nlptown/bert-base-multilingual-uncased-sentiment")
    print("✅ BERT model loaded successfully.")
except Exception as e:
    print(f"❌ Error loading BERT model: {e}")
    bert_classifier = None

# ---------------------- Preprocessing ----------------------
def preprocess_text(text):
    if not isinstance(text, str):
        return ""
    text = text.lower()
    text = re.sub(r'http\S+', '', text)
    text = re.sub(r'[^a-zA-Z\s]', '', text)
    text = ' '.join([word for word in text.split() if word not in STOPWORDS])
    return text

# ---------------------- Apply SVM Pipeline ----------------------
def apply_svm_pipeline(df):
    if svm_model is None or vectorizer is None:
        print("❌ SVM model not loaded.")
        df["svm_prediction"] = -1
        df["svm_sentiment"] = "Error"
        return df
    
    try:
        # Transform text using TF-IDF
        X = vectorizer.transform(df["cleaned_text"])
        # Predict using SVM
        predictions = svm_model.predict(X)
        df["svm_prediction"] = predictions
        df["svm_sentiment"] = df["svm_prediction"].map({0: "negative", 1: "neutral", 2: "positive"})
        print("✅ SVM Sentiment Analysis applied successfully.")
    except Exception as e:
        print(f"❌ Error applying SVM pipeline: {e}")
        df["svm_prediction"] = -1
        df["svm_sentiment"] = "Error"
    return df

# ---------------------- Apply Logistic Regression ----------------------
def apply_lr_pipeline(df):
    if lr_model is None or vectorizer is None:
        print("❌ Logistic Regression model not loaded.")
        df["lr_prediction"] = -1
        df["lr_sentiment"] = "Error"
        return df
    
    try:
        # Transform text using TF-IDF
        X = vectorizer.transform(df["cleaned_text"])
        # Predict using Logistic Regression
        predictions = lr_model.predict(X)
        df["lr_prediction"] = predictions
        df["lr_sentiment"] = df["lr_prediction"].map({0: "negative", 1: "neutral", 2: "positive"})
        print("✅ Logistic Regression Sentiment Analysis applied successfully.")
    except Exception as e:
        print(f"❌ Error applying Logistic Regression pipeline: {e}")
        df["lr_prediction"] = -1
        df["lr_sentiment"] = "Error"
    return df

# ---------------------- Apply BERT ----------------------
def map_bert_sentiment(score):
    try:
        score = int(score.split()[0])  # Extract the number from "X stars"
        if score <= 2:
            return "negative"
        elif score == 3:
            return "neutral"
        else:
            return "positive"
    except:
        return "Error"

def apply_bert_model(df):
    if bert_classifier is None:
        print("❌ BERT model not loaded.")
        df["bert_sentiment"] = "Error"
        return df
    
    try:
        # Apply BERT model and map to standard sentiment labels
        df["bert_raw"] = df["cleaned_text"].apply(
            lambda x: bert_classifier(x)[0]["label"] if x else "Error"
        )
        df["bert_sentiment"] = df["bert_raw"].apply(map_bert_sentiment)
        print("✅ BERT Sentiment Analysis applied successfully.")
    except Exception as e:
        print(f"❌ Error applying BERT model: {e}")
        df["bert_sentiment"] = "Error"
    return df

# ---------------------- Analyze CSV File ----------------------
def analyze_csv(filepath):
    try:
        # Read CSV file
        df = pd.read_csv(filepath)
        
        # Check if required columns exist
        if 'text' not in df.columns:
            print("❌ CSV file must contain a 'text' column")
            return None
        
        # Preprocess text
        df["cleaned_text"] = df["text"].apply(preprocess_text)
        
        # Apply sentiment analysis
        df = apply_svm_pipeline(df)
        df = apply_lr_pipeline(df)
        df = apply_bert_model(df)
        
        # Calculate model agreement
        df["model_agreement"] = df.apply(
            lambda row: "All Agree" if row["svm_sentiment"] == row["lr_sentiment"] == row["bert_sentiment"]
            else "Two Agree" if (row["svm_sentiment"] == row["lr_sentiment"] or 
                               row["lr_sentiment"] == row["bert_sentiment"] or 
                               row["svm_sentiment"] == row["bert_sentiment"])
            else "No Agreement",
            axis=1
        )
        
        # Save results
        results_file = os.path.join(os.path.dirname(filepath), "analysis_results.csv")
        df.to_csv(results_file, index=False)
        print(f"✅ Results saved to {results_file}")
        
        return df.to_dict(orient="records")
    
    except Exception as e:
        print(f"❌ Error analyzing CSV file: {e}")
        return None

# ---------------------- Generate Recommendations ----------------------
def generate_recommendations(sentiment_data):
    """Generate personalized mental health recommendations based on sentiment analysis results."""
    positive = sentiment_data.get("positive", 0)
    negative = sentiment_data.get("negative", 0)
    neutral = sentiment_data.get("neutral", 0)
    total = positive + negative + neutral

    if total == 0:
        return ["No data available for analysis."]

    recommendations = []

    # Calculate percentages
    positive_percent = (positive / total) * 100 if total > 0 else 0
    negative_percent = (negative / total) * 100 if total > 0 else 0
    neutral_percent = (neutral / total) * 100 if total > 0 else 0

    # Mental Health Content Analysis
    if negative_percent > 50:
        recommendations.extend([
            "High prevalence of negative sentiment detected. Consider implementing more positive reinforcement strategies.",
            "Content shows significant negative emotional patterns. Recommend incorporating more uplifting and supportive content.",
            "Consider adding mental health resources and support information to help address negative emotions.",
            "Suggest implementing regular mental health check-ins and support mechanisms.",
            "Content indicates potential need for professional mental health support. Consider providing access to counseling services."
        ])
    elif positive_percent > 50:
        recommendations.extend([
            "Strong positive sentiment detected. Continue fostering this positive environment.",
            "Content shows healthy emotional patterns. Maintain current supportive strategies.",
            "Consider sharing success stories and positive coping mechanisms to reinforce good mental health practices.",
            "Content indicates good mental health awareness. Continue promoting positive mental health habits.",
            "Suggest implementing peer support groups to maintain positive mental health momentum."
        ])
    else:
        recommendations.extend([
            "Mixed emotional patterns detected. Consider implementing balanced mental health support strategies.",
            "Content shows varied emotional responses. Recommend personalized mental health support approaches.",
            "Consider implementing regular mental health awareness sessions.",
            "Suggest creating a comprehensive mental health support plan.",
            "Content indicates need for diverse mental health resources. Consider providing multiple support channels."
        ])

    # Specific Mental Health Interventions
    if negative > positive:
        recommendations.extend([
            "Implement immediate mental health support interventions.",
            "Consider providing access to crisis support services.",
            "Recommend regular mental health check-ins and monitoring.",
            "Suggest implementing stress management workshops.",
            "Consider providing mindfulness and relaxation resources."
        ])
    elif positive > neutral:
        recommendations.extend([
            "Continue current mental health support strategies.",
            "Consider expanding positive mental health initiatives.",
            "Recommend sharing success stories and positive coping mechanisms.",
            "Suggest implementing peer support programs.",
            "Consider organizing mental health awareness events."
        ])
    else:
        recommendations.extend([
            "Implement balanced mental health support programs.",
            "Consider providing diverse mental health resources.",
            "Recommend regular mental health assessments.",
            "Suggest implementing personalized support plans.",
            "Consider creating a comprehensive mental health support network."
        ])

    # Model Performance Insights
    if sentiment_data.get("model_agreement", {}).get("all_agree", 0) / total > 0.7:
        recommendations.extend([
            "High model agreement indicates reliable sentiment analysis results.",
            "Consistent sentiment patterns suggest clear mental health trends.",
            "Strong agreement across models indicates clear emotional patterns."
        ])
    elif sentiment_data.get("model_agreement", {}).get("all_agree", 0) / total < 0.3:
        recommendations.extend([
            "Low model agreement suggests complex emotional patterns.",
            "Consider implementing more detailed mental health assessments.",
            "Varied sentiment patterns indicate need for personalized support."
        ])

    # Additional Mental Health Resources
    recommendations.extend([
        "Consider providing access to mental health professionals.",
        "Recommend implementing regular mental health workshops.",
        "Suggest creating a mental health resource library.",
        "Consider establishing peer support networks.",
        "Recommend providing mental health self-assessment tools."
    ])

    return recommendations



