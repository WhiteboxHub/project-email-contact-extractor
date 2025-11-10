import spacy
from bs4 import BeautifulSoup
import phonenumbers
import re
from email.utils import parseaddr
from icalendar import Calendar

class NERContactExtractor:
    def __init__(self, model="en_core_web_sm"):
        self.nlp = spacy.load(model)
        self.email_regex = re.compile(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+")
        self.linkedin_regex = re.compile(
            r"https?://(?:[a-z]{2,3}\.)?linkedin\.com/in/([a-zA-Z0-9\-_]+)",
            re.IGNORECASE
        )
        self.url_pattern = re.compile(r'https?://[^\s"\']+')

    def clean_body(self, html):
        soup = BeautifulSoup(html, "html.parser")
        text = soup.get_text(separator="\n")
        text = re.split(r"On .+ wrote:", text)[0]
        return text.strip()

    def extract_contacts(self, email_message, source_email=None):
        calendar_email = self._extract_calendar_email(email_message)

        raw_body = self._get_email_body(email_message)
        body = self.clean_body(raw_body)
        doc = self.nlp(body)

        name = self._extract_name(doc, body, email_message=email_message)
        email = calendar_email or self._extract_email(body)
        phone = self._extract_phone(body)
        linkedin = self._extract_linkedin(body)
        sender_email = email_message.get("From")
        company = self._extract_company(doc, body, email=email, linkedin=linkedin, sender_email=sender_email)
        return {
            "name": name,
            "email": email,
            "phone": phone,
            "company": company,
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
    def _extract_calendar_email(self, email_message):
        """Extract ORGANIZER and ATTENDEE emails from calendar invites (regex only)."""
        emails = set()

        if email_message.is_multipart():
            for part in email_message.walk():
                if part.get_content_type() == "text/calendar":
                    try:
                        payload = part.get_payload(decode=True).decode("utf-8", errors="ignore")

                        for match in re.findall(r"ORGANIZER.*mailto:([^ \r\n]+)", payload, re.IGNORECASE):
                            emails.add(match.lower())

                        for match in re.findall(r"ATTENDEE.*mailto:([^ \r\n]+)", payload, re.IGNORECASE):
                            emails.add(match.lower())

                    except Exception as e:
                        print("Calendar parsing error:", e)

        if not emails:
            for header in ["Sender", "Reply-To", "From"]:
                if header in email_message:
                    _, addr = parseaddr(email_message.get(header))
                    if addr and "noreply" not in addr.lower():
                        emails.add(addr.lower())

        return list(emails) if emails else None


    def extract_contacts(self, email_message, source_email=None):
        calendar_emails = self._extract_calendar_email(email_message)

        raw_body = self._get_email_body(email_message)
        body = self.clean_body(raw_body)
        doc = self.nlp(body)

        name = self._extract_name(doc, body, email_message=email_message)

        email = (calendar_emails[0] if calendar_emails else None) or self._extract_email(body)

        phone = self._extract_phone(body)
        linkedin = self._extract_linkedin(body)
        sender_email = email_message.get("From")
        company = self._extract_company(doc, body, email=email, linkedin=linkedin, sender_email=sender_email)

        return {
            "name": name,
            "email": email,
            "calendar_emails": calendar_emails,  
            "phone": phone,
            "company": company,
            "linkedin_id": linkedin,
            "source": source_email if source_email else None
        }

    def _extract_name(self, doc, text, email_message=None):
        if email_message:
            from_header = email_message.get("From")
            if from_header:
                name, _ = parseaddr(from_header)
                if name and len(name.split()) <= 3:
                    return name.strip()

        for ent in doc.ents:
            if ent.label_ == "PERSON" and len(ent.text.split()) <= 3:
                return ent.text.strip()

        match = re.search(r"(Thanks|Regards|Best),?\s*\n([A-Z][a-z]+ [A-Z][a-z]+)", text)
        if match:
            return match.group(2).strip()

        return None

    def _extract_email(self, text):
        match = re.search(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+", text)
        return match.group(0) if match else None

    def _extract_phone(self, text):
        for match in phonenumbers.PhoneNumberMatcher(text, "US"):
            return phonenumbers.format_number(match.number, phonenumbers.PhoneNumberFormat.E164)
        return None

    def _extract_linkedin(self, text):
        match = self.linkedin_regex.search(text)
        if match:
            return match.group(1)  
        return None


    class YourClass:
        def __init__(self):
            self.linkedin_regex = re.compile(
                r'https?://(?:www\.)?linkedin\.com/in/([A-Za-z0-9-]+)',
                re.IGNORECASE
            )

    def _extract_company(self, doc, text, email=None, linkedin=None, sender_email=None):
        """
        Extract company name from email domains.
        Example: john.doe@infosys.com -> Infosys
                recruiter@inviter.ai -> Inviter
        """

        blacklist = {"gmail", "yahoo", "hotmail", "outlook", "protonmail", "aws"}

        def get_from_email(e):
            if e and "@" in e:
                domain_part = e.split("@")[1]  
                domain_name = domain_part.split(".")[0] 
                if domain_name.lower() not in blacklist:
                    return domain_name.replace("-", " ").title()
            return None

    
        company = get_from_email(sender_email) or get_from_email(email)
        return company