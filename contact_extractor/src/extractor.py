import spacy
from bs4 import BeautifulSoup
import phonenumbers
import re

class NERContactExtractor:
    def __init__(self, model="en_core_web_trf"):
        self.nlp = spacy.load(model)

    def clean_body(self, html):
        soup = BeautifulSoup(html, "html.parser")
        text = soup.get_text(separator="\n")
        # Remove quoted replies, footers, etc. (simple heuristic)
        text = re.split(r"On .+ wrote:", text)[0]
        return text.strip()

    def extract_contacts(self, email_message, source_email=None):
        """
        Extract contact information from an email message.
        Returns a dict with keys: name, email, phone, company, website, linkedin_id, source.
        The 'source' field indicates which candidate/source email account this contact was extracted for.
        """
        body = self.clean_body(self._get_email_body(email_message))
        doc = self.nlp(body)
        entities = {ent.label_: ent.text for ent in doc.ents}
        # Email and phone fallback
        email = self._extract_email(body)
        phone = self._extract_phone(body)
        linkedin = self._extract_linkedin(body)
        company = entities.get("ORG") or self._extract_company(body, source_email)
        website = entities.get("URL") or self._extract_website(body)
        name = entities.get("PERSON")
        # Always include the source email (the candidate mailbox being processed)
        return {
            "name": name,
            "email": email,
            "phone": phone,
            "company": company,
            "website": website,
            "linkedin_id": linkedin,
            "source": source_email if source_email else None
        }

    def _get_email_body(self, email_message):
        # (reuse your existing logic)
        if email_message.is_multipart():
            for part in email_message.walk():
                if part.get_content_type() == 'text/plain':
                    return part.get_payload(decode=True).decode('utf-8', errors='ignore')
        else:
            return email_message.get_payload(decode=True).decode('utf-8', errors='ignore')
        return ""

    def _extract_email(self, text):
        match = re.search(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+", text)
        return match.group(0) if match else None

    def _extract_phone(self, text):
        for match in phonenumbers.PhoneNumberMatcher(text, "US"):
            return phonenumbers.format_number(match.number, phonenumbers.PhoneNumberFormat.E164)
        return None

    def _extract_company(self, text, sender_email):
        # First try to find company name in signature
        company_patterns = [
            r'at\s+([A-Z][a-zA-Z\s&]+)',
            r'([A-Z][a-zA-Z\s&]+)\s*Inc',
            r'([A-Z][a-zA-Z\s&]+)\s*LLC',
        ]
        for pattern in company_patterns:
            match = re.search(pattern, text)
            if match:
                return match.group(1).strip()
        # Fallback to domain name
        if sender_email and '@' in sender_email:
            domain = sender_email.split('@')[1]
            return domain.split('.')[0].capitalize()
        return None

    def _extract_website(self, text):
        url_pattern = r'https?://[^\s/$.?#].[^\s]*'
        matches = re.findall(url_pattern, text)
        for url in matches:
            if "linkedin.com" not in url:
                return url
        return None

    def _extract_linkedin(self, text):
        # Look for LinkedIn URLs in the text
        linkedin_pattern = r'https?://(?:[a-z]{2,3}\.)?linkedin\.com/in/([a-zA-Z0-9\-_]+)'
        match = re.search(linkedin_pattern, text)
        if match:
            return match.group(1)  # This is the LinkedIn ID
        # Fallback to previous patterns if needed
        match_url = re.search(r"https?://(www\.)?linkedin\.com/in/[a-zA-Z0-9\-_]+", text)
        if match_url:
            return match_url.group(0)
        return None