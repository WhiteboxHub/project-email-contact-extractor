import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
import joblib
import os

DATA_PATH = "../data/labeled_emails.csv"
MODEL_DIR = "../models"
CLASSIFIER_PATH = os.path.join(MODEL_DIR, "classifier.pkl")
VECTORIZER_PATH = os.path.join(MODEL_DIR, "vectorizer.pkl")

os.makedirs(MODEL_DIR, exist_ok=True)

df = pd.read_csv(DATA_PATH)

df['text'] = df['subject'].fillna('') + " " + df['body'].fillna('') + " " + df['from_email'].fillna('')

vectorizer = TfidfVectorizer(max_features=5000)
X = vectorizer.fit_transform(df['text'])

y = df['label'] 

clf = LogisticRegression(max_iter=1000)
clf.fit(X, y)

joblib.dump(clf, CLASSIFIER_PATH)
joblib.dump(vectorizer, VECTORIZER_PATH)

