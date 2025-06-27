import joblib # type: ignore
import os

class MLRecruiterFilter:
    def __init__(self, model_dir):
        self.classifier = joblib.load(os.path.join(model_dir, "classifier.pkl"))
        self.vectorizer = joblib.load(os.path.join(model_dir, "vectorizer.pkl"))

    def is_recruiter(self, subject, body, from_email):
        features = self.vectorizer.transform([f"{subject} {body} {from_email}"])
        return self.classifier.predict(features)[0] == 1

    def filter_recruiter_emails(self, emails, extractor):
        filtered = []
        for email_data in emails:
            subject = email_data['message'].get('Subject', '')
            body = extractor.clean_body(extractor._get_email_body(email_data['message']))
            from_email = email_data['message'].get('From', '')
            if self.is_recruiter(subject, body, from_email):
                filtered.append(email_data)
        return filtered