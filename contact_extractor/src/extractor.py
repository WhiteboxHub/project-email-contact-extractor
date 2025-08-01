# import spacy
# from bs4 import BeautifulSoup
# import phonenumbers
# import re

# class NERContactExtractor:
#     def __init__(self, model="en_core_web_trf"):  # BETTER NER
#         self.nlp = spacy.load(model)

#     def clean_body(self, html):
#         soup = BeautifulSoup(html, "html.parser")
#         text = soup.get_text(separator="\n")
#         # Remove quoted replies, footers, etc. (simple heuristic)
#         text = re.split(r"On .+ wrote:", text)[0]
#         return text.strip()

#     def extract_contacts(self, email_message, source_email=None):
#         """
#         Extract contact information from an email message.
#         Returns a dict with keys: name, email, phone, company, website, linkedin_id, source.
#         The 'source' field indicates which candidate/source email account this contact was extracted for.
#         """
#         body = self.clean_body(self._get_email_body(email_message))
#         doc = self.nlp(body)
#         entities = {ent.label_: ent.text for ent in doc.ents}
#         # Email and phone fallback
#         email = self._extract_email(body)
#         phone = self._extract_phone(body)
#         linkedin = self._extract_linkedin(body)
#         company = entities.get("ORG") or self._extract_company(body, source_email)
#         website = entities.get("URL") or self._extract_website(body)
#         name = entities.get("PERSON")
#         # Always include the source email (the candidate mailbox being processed)
#         return {
#             "name": name,
#             "email": email,
#             "phone": phone,
#             "company": company,
#             "website": website,
#             "linkedin_id": linkedin,
#             "source": source_email if source_email else None
#         }

#     def _get_email_body(self, email_message):
#         # (reuse your existing logic)
#         if email_message.is_multipart():
#             for part in email_message.walk():
#                 if part.get_content_type() == 'text/plain':
#                     return part.get_payload(decode=True).decode('utf-8', errors='ignore')
#         else:
#             return email_message.get_payload(decode=True).decode('utf-8', errors='ignore')
#         return ""

#     def _extract_email(self, text):
#         match = re.search(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+", text)
#         return match.group(0) if match else None

#     def _extract_phone(self, text):
#         for match in phonenumbers.PhoneNumberMatcher(text, "US"):
#             return phonenumbers.format_number(match.number, phonenumbers.PhoneNumberFormat.E164)
#         return None

#     def _extract_company(self, text, sender_email):
#         # First try to find company name in signature
#         company_patterns = [
#             r'at\s+([A-Z][a-zA-Z\s&]+)',
#             r'([A-Z][a-zA-Z\s&]+)\s*Inc',
#             r'([A-Z][a-zA-Z\s&]+)\s*LLC',
#         ]
#         for pattern in company_patterns:
#             match = re.search(pattern, text)
#             if match:
#                 return match.group(1).strip()
#         # Fallback to domain name
#         if sender_email and '@' in sender_email:
#             domain = sender_email.split('@')[1]
#             return domain.split('.')[0].capitalize()
#         return None

#     def _extract_website(self, text):
#         url_pattern = r'https?://[^\s/$.?#].[^\s]*'
#         matches = re.findall(url_pattern, text)
#         for url in matches:
#             if "linkedin.com" not in url:
#                 return url
#         return None

#     def _extract_linkedin(self, text):
#         # Look for LinkedIn URLs in the text
#         linkedin_pattern = r'https?://(?:[a-z]{2,3}\.)?linkedin\.com/in/([a-zA-Z0-9\-_]+)'
#         match = re.search(linkedin_pattern, text)
#         if match:
#             return match.group(1)  # This is the LinkedIn ID
#         # Fallback to previous patterns if needed
#         match_url = re.search(r"https?://(www\.)?linkedin\.com/in/[a-zA-Z0-9\-_]+", text)
#         if match_url:
#             return match_url.group(0)
#         return None


# import spacy
# from bs4 import BeautifulSoup
# import phonenumbers
# import re

# class NERContactExtractor:
#     def __init__(self, model="en_core_web_sm"):  # upgrade to en_core_web_trf if possible
#         self.nlp = spacy.load(model)

#     def clean_body(self, html):
#         soup = BeautifulSoup(html, "html.parser")
#         text = soup.get_text(separator="\n")
#         # Remove quoted replies and signatures
#         text = re.split(r"On .+ wrote:", text)[0]
#         return text.strip()

#     def extract_contacts(self, email_message, source_email=None):
#         body = self.clean_body(self._get_email_body(email_message))
#         doc = self.nlp(body)

#         name = self._extract_name(doc, body)
#         email = self._extract_email(body)
#         phone = self._extract_phone(body)
#         linkedin = self._extract_linkedin(body)
#         company = self._extract_company(doc, body, email, linkedin, source_email)
#         website = self._extract_website(body)

#         return {
#             "name": name,
#             "email": email,
#             "phone": phone,
#             "company": company,
#             "website": website,
#             "linkedin_id": linkedin,
#             "source": source_email if source_email else None
#         }

#     def _get_email_body(self, email_message):
#         if email_message.is_multipart():
#             for part in email_message.walk():
#                 if part.get_content_type() == 'text/plain':
#                     return part.get_payload(decode=True).decode('utf-8', errors='ignore')
#         else:
#             return email_message.get_payload(decode=True).decode('utf-8', errors='ignore')
#         return ""

#     def _extract_name(self, doc, text):
#         # Priority: NER > Signature
#         names = [ent.text for ent in doc.ents if ent.label_ == "PERSON"]
#         if names:
#             return names[0]
#         # Fallback: signature line
#         match = re.search(r"(Thanks|Regards|Best),?\s*\n([A-Z][a-z]+ [A-Z][a-z]+)", text)
#         if match:
#             return match.group(2)
#         return None

#     def _extract_email(self, text):
#         # Improved multiple match fallback
#         matches = re.findall(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+", text)
#         for email in matches:
#             if not any(kw in email for kw in ["noreply", "do-not-reply", "donotreply", "autobot", "support"]):
#                 return email
#         return matches[0] if matches else None

#     def _extract_phone(self, text):
#         for match in phonenumbers.PhoneNumberMatcher(text, "US"):
#             return phonenumbers.format_number(match.number, phonenumbers.PhoneNumberFormat.E164)
#         return None

#     def _extract_linkedin(self, text):
#         pattern = r"https?://(?:[a-z]{2,3}\.)?linkedin\.com/in/[a-zA-Z0-9\-_]+"
#         match = re.search(pattern, text)
#         return match.group(0) if match else None

#     def _extract_company(self, doc, text, email=None, linkedin=None, sender_email=None):
#         orgs = [ent.text for ent in doc.ents if ent.label_ == "ORG"]
#         if orgs:
#             return orgs[0]

#         # Signature fallback
#         match = re.search(r"\n([A-Z][a-zA-Z&.\s]+)(Inc|LLC|Ltd|Technologies|Solutions)?", text)
#         if match:
#             return match.group(1).strip()

#         # LinkedIn-based fallback
#         if linkedin:
#             match = re.search(r"linkedin\.com/in/([a-zA-Z0-9\-]+)", linkedin)
#             if match:
#                 parts = match.group(1).split('-')
#                 if len(parts) >= 2:
#                     return parts[-1].capitalize()

#         # Email domain fallback
#         if email and "@" in email:
#             domain = email.split('@')[1].split('.')[0]
#             if domain.lower() not in ["gmail", "yahoo", "hotmail", "outlook", "protonmail"]:
#                 return domain.capitalize()

#         # Fallback from sender email
#         if sender_email and '@' in sender_email:
#             domain = sender_email.split('@')[1].split('.')[0]
#             return domain.capitalize()

#         return None

#     def _extract_website(self, text):
#         url_pattern = r'https?://[^\s"\']+'
#         urls = re.findall(url_pattern, text)
#         for url in urls:
#             if "linkedin.com" not in url and "unsubscribe" not in url:
#                 return url
#         return None





import spacy
from bs4 import BeautifulSoup
import phonenumbers
import re
from email.utils import parseaddr

class NERContactExtractor:
    #def __init__(self, model="en_core_web_sm"):

    def __init__(self, model="en_core_web_sm"):
        self.nlp = spacy.load(model)
        self.email_regex = re.compile(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+")
        self.linkedin_regex = re.compile(r"https?://(?:[a-z]{2,3}\.)?linkedin\.com/in/[a-zA-Z0-9\-_]+")
        self.url_pattern = re.compile(r'https?://[^\s"\']+')

    def clean_body(self, html):
        soup = BeautifulSoup(html, "html.parser")
        text = soup.get_text(separator="\n")
        # Remove quoted replies like "On Jan 1, 2023, John wrote:"
        text = re.split(r"On .+ wrote:", text)[0]
        return text.strip()

    def extract_contacts(self, email_message, source_email=None):
        raw_body = self._get_email_body(email_message)
        body = self.clean_body(raw_body)
        doc = self.nlp(body)

        name = self._extract_name(doc, body, email_message=email_message)
        email = self._extract_email(body)
        phone = self._extract_phone(body)
        linkedin = self._extract_linkedin(body)
        sender_email = email_message.get("From")
        company = self._extract_company(doc, body, email=email, linkedin=linkedin, sender_email=sender_email)
        website = self._extract_website(body)

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
        if email_message.is_multipart():
            for part in email_message.walk():
                if part.get_content_type() == 'text/plain' and part.get_payload(decode=True):
                    return part.get_payload(decode=True).decode('utf-8', errors='ignore')
        else:
            return email_message.get_payload(decode=True).decode('utf-8', errors='ignore')
        return ""

    def _extract_name(self, doc, text, email_message=None):
        # 1. Try From header
        if email_message:
            from_header = email_message.get("From")
            if from_header:
                name, _ = parseaddr(from_header)
                if name and len(name.split()) <= 3:
                    return name.strip()

        # 2. Try NER
        for ent in doc.ents:
            if ent.label_ == "PERSON" and len(ent.text.split()) <= 3:
                return ent.text.strip()

        # 3. Signature fallback
        match = re.search(r"(Thanks|Regards|Best),?\s*\n([A-Z][a-z]+ [A-Z][a-z]+)", text)
        if match:
            return match.group(2).strip()

        return None

    def _extract_email(self, text):
        matches = self.email_regex.findall(text)
        for email in matches:
            if not any(kw in email.lower() for kw in ["noreply", "donotreply", "autobot", "support"]):
                return email
        return matches[0] if matches else None

    def _extract_phone(self, text):
        for match in phonenumbers.PhoneNumberMatcher(text, "US"):
            return phonenumbers.format_number(match.number, phonenumbers.PhoneNumberFormat.E164)
        return None

    def _extract_linkedin(self, text):
        match = self.linkedin_regex.search(text)
        return match.group(0) if match else None

    def _extract_company(self, doc, text, email=None, linkedin=None, sender_email=None):
        # 1. Try ORG entity
        for ent in doc.ents:
            if ent.label_ == "ORG":
                return ent.text.strip()

        # 2. Signature line fallback
        match = re.search(r"\n([A-Z][a-zA-Z&.\s]+)(Inc|LLC|Ltd|Technologies|Solutions)?", text)
        if match:
            return match.group(1).strip()

        # 3. From email domain
        if sender_email and '@' in sender_email:
            domain = sender_email.split('@')[1].split('.')[0]
            if domain.lower() not in ["gmail", "yahoo", "hotmail", "outlook", "protonmail"]:
                return domain.replace("-", " ").title()

        # 4. LinkedIn slug fallback
        if linkedin:
            match = re.search(r"linkedin\.com/in/([a-zA-Z0-9\-]+)", linkedin)
            if match:
                slug_parts = match.group(1).split('-')
                if len(slug_parts) >= 2:
                    return slug_parts[-1].capitalize()

        # 5. Email domain fallback
        if email and "@" in email:
            domain = email.split('@')[1].split('.')[0]
            if domain.lower() not in ["gmail", "yahoo", "hotmail", "outlook", "protonmail"]:
                return domain.replace("-", " ").title()

        return None

    def _extract_website(self, text):
        urls = self.url_pattern.findall(text)
        for url in urls:
            if "linkedin.com" not in url and "unsubscribe" not in url:
                return url
        return None
