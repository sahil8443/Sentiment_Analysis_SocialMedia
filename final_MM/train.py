import pandas as pd
import joblib
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.svm import SVC
from sklearn.linear_model import LogisticRegression
import sys
sys.stdout.reconfigure(encoding='utf-8')


# Load dataset with proper encoding
df = pd.read_csv("LabeledText.csv", encoding="ISO-8859-1")

# Drop missing values to avoid errors
df = df.dropna(subset=["Caption", "LABEL"])

# Ensure all labels exist in the mapping
label_mapping = {"positive": 1, "negative": 0, "neutral": 2}
df = df[df["LABEL"].isin(label_mapping.keys())]  # Remove unexpected labels

# Convert labels to numerical values
df["Label_Num"] = df["LABEL"].map(label_mapping)

# Split data
X_train, X_test, y_train, y_test = train_test_split(df["Caption"], df["Label_Num"], test_size=0.2, random_state=42)

# Convert text to TF-IDF vectors
vectorizer = TfidfVectorizer(max_features=10000, ngram_range=(1,2), min_df=2)
X_train_tfidf = vectorizer.fit_transform(X_train)
X_test_tfidf = vectorizer.transform(X_test)

# Train SVM model
svm_model = SVC(kernel="rbf", C=2.0, gamma='scale', class_weight='balanced', probability=True)
svm_model.fit(X_train_tfidf, y_train)

# Train Logistic Regression model
lr_model = LogisticRegression(multi_class='multinomial', class_weight='balanced', max_iter=1000)
lr_model.fit(X_train_tfidf, y_train)

# Save models and vectorizer
joblib.dump(svm_model, "svm_sentiment_model.pkl")
joblib.dump(lr_model, "lr_sentiment_model.pkl")
joblib.dump(vectorizer, "tfidf_vectorizer.pkl")

print("✅ SVM, Logistic Regression models and vectorizer saved successfully!")
