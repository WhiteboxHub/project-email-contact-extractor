import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
import joblib

df = pd.read_csv("../data/labeled_emails.csv")
df['text'] = df['subject'] + " " + df['body'] + " " + df['from_email']

vectorizer = TfidfVectorizer(max_features=5000)
X = vectorizer.fit_transform(df['text'])
y = df['label']  

clf = LogisticRegression()
clf.fit(X, y)

joblib.dump(clf, "../models/classifier.pkl")
joblib.dump(vectorizer, "../models/vectorizer.pkl")
