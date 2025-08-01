# import pandas as pd
# from sklearn.feature_extraction.text import TfidfVectorizer
# from sklearn.linear_model import LogisticRegression
# import joblib

# # Load your labeled data (CSV with columns: subject, body, from_email, label)
# df = pd.read_csv("../data/labeled_emails.csv")
# df['text'] = df['subject'] + " " + df['body'] + " " + df['from_email']

# vectorizer = TfidfVectorizer(max_features=5000)
# X = vectorizer.fit_transform(df['text'])
# y = df['label']  # 1 = recruiter/vendor, 0 = junk

# clf = LogisticRegression()
# clf.fit(X, y)

# joblib.dump(clf, "../models/classifier.pkl")
# joblib.dump(vectorizer, "../models/vectorizer.pkl")

import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
import joblib
import os

# File paths
DATA_PATH = "../data/labeled_emails.csv"
MODEL_DIR = "../models"
CLASSIFIER_PATH = os.path.join(MODEL_DIR, "classifier.pkl")
VECTORIZER_PATH = os.path.join(MODEL_DIR, "vectorizer.pkl")

# Ensure model directory exists
os.makedirs(MODEL_DIR, exist_ok=True)

# Step 1: Load labeled dataset
print("📥 Loading dataset...")
df = pd.read_csv(DATA_PATH)

# Step 2: Combine features into a single text column
df['text'] = df['subject'].fillna('') + " " + df['body'].fillna('') + " " + df['from_email'].fillna('')

# Step 3: Vectorize text using TF-IDF
print("🧠 Vectorizing text...")
vectorizer = TfidfVectorizer(max_features=5000)
X = vectorizer.fit_transform(df['text'])

# Step 4: Prepare labels
y = df['label']  # 1 = recruiter/vendor, 0 = junk/non-recruiter

# Step 5: Train logistic regression classifier
print("🤖 Training classifier...")
clf = LogisticRegression(max_iter=1000)
clf.fit(X, y)

# Step 6: Save model and vectorizer
joblib.dump(clf, CLASSIFIER_PATH)
joblib.dump(vectorizer, VECTORIZER_PATH)

print(f"✅ Model and vectorizer saved to '{MODEL_DIR}'")
