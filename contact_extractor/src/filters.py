
import re
import logging

logger = logging.getLogger("extractor")

class EmailFilter:
    def filter_recruiter_emails(self, emails, extractor):
        filtered = []
        recruiter_keywords = extractor.recruiter_keywords

        for email_data in emails:
            msg = email_data["message"]
            sender = msg.get("from", "")
            subject = msg.get("subject", "")
            body = msg.get("body", "")

            if extractor._matches_blacklist(sender):
                continue

            keyword_found = any(
                keyword.lower() in (sender + subject + body).lower()
                for keyword in recruiter_keywords
            )

            if keyword_found:
                filtered.append(email_data)
            else:
                logger.info(f"Email from {sender} skipped: no recruiter keywords in subject, sender name, sender email, or body.")

        return filtered
