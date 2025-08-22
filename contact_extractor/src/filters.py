import joblib
import os
import re
import logging
from typing import Dict, List, Set

class MLRecruiterFilter:
    def __init__(self, model_dir):
        self.classifier = joblib.load(os.path.join(model_dir, "classifier.pkl"))
        self.vectorizer = joblib.load(os.path.join(model_dir, "vectorizer.pkl"))
        self.logger = logging.getLogger(__name__)
        self._initialize_filter_lists()

    def _initialize_filter_lists(self):
        self.blacklist_keywords = {
            "noreply", "no-reply", "donotreply", "do-not-reply",
            "autoresponder", "mailer-daemon", "bounce", "autoemail",
            "autobot", "bot", "notifications", "notification",
            "support", "helpdesk", "system", "admin", "updates",
            "reminder", "passwordreset", "alerts", "security",
            "confirm", "newsletter", "subscribe", "unsubscribe",
            "bulk", "campaign", "ads", "advertise", "offers",
            "promotions", "jobs", "jobalerts", "careers", "hr",
            "info", "contact", "noreplymail", "noreplies",
            "image", "team", "recruiting", "communications", "data",
            "marketing", "customer", "enterprise", "inmail", "dse",
            "zrc-ptv", "ltxstudio", "aggregated", "truthteam",
            "customercare", "echosign", "hello"
        }

        self.personal_domains = {
            "gmail.com", "yahoo.com", "outlook.com", "hotmail.com",
            "aol.com", "icloud.com", "mail.com", "live.com", "msn.com",
            "protonmail.com", "zoho.com", "yandex.com", "gmx.com",
            "qq.com", "me.com", "pm.me"
        }

        self.service_domains = {
            "amazon.com", "google.com", "facebook.com", "linkedin.com",
            "github.com", "slack.com", "zoom.us", "twitter.com",
            "microsoft.com", "apple.com", "workablemail.com", "dice.com",
            "myworkday.com", "narwal.ai", "txt.voice.google.com", "email.shopify.com"
        }

        self.exact_email_blacklist = {
            "teamzoom@zoom.us", "ops@cluso.com", "recruiter@softquip.com",
            "requirements@gainamerica.net", "assistant@glider.ai",
            "good-people@mail.beehiiv.com", "echosign@echosign.com",
            "aggregated@lensa.com", "truthteam@email.truthsocial.com",
            "remove@greattechglobal.com", "username@narwal.ai.",
            "wi3351252t@wipro.com", "hello@v3.idibu.com",
            "e.linkedin.com", 
        }

        self.junk_pattern = re.compile(
            r'^(no-?reply|auto(responder|bot)|.*alert.*|.*noreply.*|.*notifications?)@',
            re.IGNORECASE
        )


    def _extract_clean_email(self, from_header: str) -> str:

        if not from_header:
            return ""
        email_match = re.search(
            r'(?:<|\(|^)([\w\.-]+@[\w\.-]+)(?:>|\)|$)', 
            from_header,
            re.IGNORECASE
        )
        return email_match.group(1).lower() if email_match else ""

    def should_ignore_email(self, email: str) -> bool:

        email = email.lower().strip()
        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            return True  

        if email in self.exact_email_blacklist:
            return True

        local_part, domain = email.split("@", 1)

        if any(kw in local_part for kw in self.blacklist_keywords):
            return True

        if domain in self.personal_domains or domain in self.service_domains:
            return True

        for black in self.exact_email_blacklist:
            if black in email or domain == black or local_part.startswith(black):
                return True

        return False

    def is_junk_email(self, from_header: str) -> bool:
        """Comprehensive junk detection using all specified rules"""
        email = self._extract_clean_email(from_header)
        if not email:
            return True
            
        if self.should_ignore_email(email):
            return True
            
        local_part, domain = email.split("@", 1)
        if domain in self.service_domains:
            return True
            
        if self.junk_pattern.match(email):
            return True
            
        return False

    def is_recruiter(self, subject: str, body: str, from_email: str) -> bool:
        """ML classification with full junk filtering"""
        if self.is_junk_email(from_email):
            return False
            
        features = self.vectorizer.transform([f"{subject} {body} {from_email}"])
        return self.classifier.predict(features)[0] == 1

    def filter_recruiter_emails(self, emails: List[Dict], extractor) -> List[Dict]:
        """Complete filtering pipeline"""
        filtered = []
        
        for email_data in emails:
            try:
                msg = email_data['message']
                from_header = msg.get('From', '')
                subject = msg.get('Subject', '')

                # ✅ If it's a calendar invite, bypass ML filter
                if any(part.get_content_type() == "text/calendar" for part in msg.walk()):
                    filtered.append(email_data)
                    continue

                if not self.is_junk_email(from_header):
                    body = extractor.clean_body(
                        extractor._get_email_body(msg)
                    )
                    if self.is_recruiter(subject, body, from_header):
                        filtered.append(email_data)
            except Exception as e:
                self.logger.error(f"Error processing email: {str(e)}")
                
        return filtered

    def extract_company_url(self, email: str) -> str:

        email = email.lower().strip()
        
        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            return None
            
        local_part, domain = email.split("@", 1)
        
        if domain in self.personal_domains:
            return None
            
        if any(kw in local_part for kw in self.blacklist_keywords):
            return None
            
        return f"https://{domain}"



