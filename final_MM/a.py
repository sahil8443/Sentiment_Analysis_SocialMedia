import psycopg2
import pandas as pd
import re
import nltk
from nltk.corpus import stopwords
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.svm import SVC
import joblib
from transformers import pipeline
import sys
sys.stdout.reconfigure(encoding='utf-8')


# Download NLTK stopwords
nltk.download('stopwords')

# ------------------------- 1. Retrieve Data from PostgreSQL -------------------------
def fetch_data_from_postgres():
    try:
        conn = psycopg2.connect(
            host="localhost",
            database="mind matrix",
            user="postgres",
            password="ash228637",
            port=5433  # Your PostgreSQL port
        )

        query = 'SELECT post_id, content FROM posts'  # Using "content" instead of "text"
        df = pd.read_sql(query, conn)
        conn.close()

        print("✅ Data fetched successfully from PostgreSQL.")
        print("Columns in DataFrame:", df.columns)  # Debugging step

        return df

    except Exception as e:
        print(f"❌ Error fetching data: {e}")
        return None

# ------------------------- 2. Preprocess Text Data -------------------------
def preprocess_text(text):
    text = text.lower()  # Convert to lowercase
    text = re.sub(r'http\S+', '', text)  # Remove URLs
    text = re.sub(r'[^a-zA-Z\s]', '', text)  # Remove special characters
    text = ' '.join([word for word in text.split() if word not in stopwords.words('english')])
    return text

# ------------------------- 3. Apply SVM Sentiment Analysis -------------------------
def apply_svm_model(df):
    try:
        svm_model = joblib.load("svm_sentiment_model.pkl")  
        vectorizer = joblib.load("tfidf_vectorizer.pkl")

        X_svm = vectorizer.transform(df["cleaned_text"])
        df["svm_prediction"] = svm_model.predict(X_svm)

        print("✅ SVM Sentiment Analysis applied.")
        return df

    except Exception as e:
        print(f"❌ Error applying SVM model: {e}")
        return df

# ------------------------- 4. Apply BERT Sentiment Analysis -------------------------
def apply_bert_model(df):
    try:
        bert_classifier = pipeline("text-classification", model="nlptown/bert-base-multilingual-uncased-sentiment")

        df["bert_prediction"] = df["cleaned_text"].apply(lambda x: bert_classifier(x)[0]["label"])

        print("✅ BERT Sentiment Analysis applied.")
        return df

    except Exception as e:
        print(f"❌ Error applying BERT model: {e}")
        return df

# ------------------------- 5. Store Results in CSV -------------------------
def save_results_to_csv(df, filename="sentiment_analysis_results.csv"):
    try:
        df.to_csv(filename, index=False)
        print(f"✅ Results saved to {filename}")
    except Exception as e:
        print(f"❌ Error saving results: {e}")

# ------------------------- MAIN EXECUTION -------------------------
if __name__ == "__main__":
    print("🔹 Fetching data from PostgreSQL...")
    df = fetch_data_from_postgres()

    if df is not None and not df.empty:
        print("🔹 Preprocessing text data...")
        df["cleaned_text"] = df["content"].apply(preprocess_text)  # Using "content"

        print("🔹 Applying SVM Sentiment Analysis...")
        df = apply_svm_model(df)

        print("🔹 Applying BERT Sentiment Analysis...")
        df = apply_bert_model(df)

        print("🔹 Saving results to CSV...")
        save_results_to_csv(df)

        print("✅ Sentiment analysis completed successfully!")
    else:
        print("❌ No data available. Please check your database connection and query.")


BEARER_TOKEN = "AAAAAAAAAAAAAAAAAAAAAFm7ygEAAAAATU%2FFtYtilY87Qwsbe5hSFwRNdsk%3DhG0c3ekV8JHzeYCKicSWMin4lXOu1UxttOFloLW2KQCV3jUpER"
