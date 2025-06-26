
import re
import logging
import os
import yaml
import spacy
from typing import Optional, Dict, Any

logger = logging.getLogger("extractor")

class ContactExtractor:
    def __init__(self):
        self.rules = self._load_rules()
        self.recruiter_keywords = self.rules.get("recruiter_keywords", [])
        self.signature_patterns = self.rules.get("signature_patterns", {})
        self.linkedin_patterns = self.rules.get("linkedin_patterns", [])
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except Exception as e:
            logger.error(f"Error loading spaCy model: {e}")
            self.nlp = None

        logger.info(f"Loaded rules: {self.rules.keys()}")

    def _load_rules(self):
        try:
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            rules_path = os.path.join(base_dir, 'config', 'rules.yaml')
            with open(rules_path, 'r') as file:
                return yaml.safe_load(file)
        except Exception as e:
            logger.error(f"Error loading rules: {e}")
            return {}

    def _matches_blacklist(self, email: str) -> bool:
        if not email:
            return False
        for pattern in self.rules.get("always_blacklist", []):
            if re.search(pattern, email, re.IGNORECASE):
                logger.info(f"Skipping generic sender: {email} (pattern: {pattern})")
                return True
        return False

    def _extract_linkedin(self, text: str) -> Optional[str]:
        """Extract LinkedIn profile URL from text"""
        for pattern in self.linkedin_patterns:
            matches = re.findall(pattern, text)
            if matches:
                # Clean up the URL
                url = matches[0].strip()
                if not url.startswith(('http://', 'https://')):
                    url = f"https://{url}"
                return url.split('?')[0]  # Remove any query parameters
        return None

    def _validate_email(self, email: str) -> bool:
        """Basic email validation"""
        if not email:
            return False
        return bool(re.match(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$", email))

    def _validate_phone(self, phone: str) -> bool:
        """Basic phone number validation"""
        if not phone:
            return False
        # Remove any non-digit characters
        digits = re.sub(r"[^\d]", "", phone)
        return len(digits) >= 7  # Minimum valid phone number length

    def _clean_phone(self, phone: str) -> str:
        """Format phone number consistently"""
        if not phone:
            return ""
        # Remove all non-digit characters
        digits = re.sub(r"[^\d]", "", phone)
        # Format as (XXX) XXX-XXXX if US number
        if len(digits) == 10:
            return f"({digits[:3]}) {digits[3:6]}-{digits[6:]}"
        return digits

    def _clean_name(self, name: str) -> str:
        """Clean and normalize names"""
        if not name:
            return ""
        # Remove extra whitespace and special characters
        name = re.sub(r"[^\w\s-]", "", name.strip())
        # Title case the name
        return name.title()

    def extract_contacts(self, text: str, source_email: str = None) -> Dict[str, Any]:
        if not self.nlp:
            raise RuntimeError("spaCy NLP model not initialized.")

        # Ensure text is a string
        if isinstance(text, dict):
            logger.warning("Input to extract_contacts() was a dict; converting to string")
            text = str(text)

        doc = self.nlp(text)
        name, email, phone, company, linkedin = None, None, None, None, None

        # Extract name and company using NLP
        for ent in doc.ents:
            if ent.label_ == "PERSON" and not name:
                name = self._clean_name(ent.text)
            elif ent.label_ == "ORG" and not company:
                company = ent.text.strip()

        # Extract email - more robust pattern
        email_matches = re.findall(
            r"\b[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}\b", 
            text
        )
        if email_matches:
            for em in email_matches:
                if not self._matches_blacklist(em) and self._validate_email(em):
                    email = em.lower()
                    break

        # Extract phone - more comprehensive patterns
        phone_patterns = self.signature_patterns.get("phone", [])
        for pattern in phone_patterns:
            match = re.search(pattern, text)
            if match:
                phone_candidate = match.group()
                if self._validate_phone(phone_candidate):
                    phone = self._clean_phone(phone_candidate)
                    break

        # Extract LinkedIn profile
        linkedin = self._extract_linkedin(text)

        # Fallback: If no company found via NLP, look for common patterns
        if not company:
            company_patterns = [
                r"at\s+([A-Z][a-zA-Z0-9&\-\.\s]+)(?=\s|$)",
                r"from\s+([A-Z][a-zA-Z0-9&\-\.\s]+)(?=\s|$)",
                r"company:\s*([^\n\r]+)",
                r"firm:\s*([^\n\r]+)"
            ]
            for pattern in company_patterns:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    company_candidate = match.group(1).strip()
                    if len(company_candidate.split()) < 5:  # Avoid long false positives
                        company = company_candidate
                        break

        return {
            "name": name,
            "email": email,
            "phone": phone,
            "company": company,
            "linkedin": linkedin,
            "source": source_email
        }