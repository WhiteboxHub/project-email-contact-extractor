 
import os
import json
import logging
from datetime import datetime
from typing import List, Dict

logger = logging.getLogger("storage")

class StorageManager:
    def __init__(self):
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.output_dir = os.path.join(base_dir, 'output')
        os.makedirs(self.output_dir, exist_ok=True)

    def _clean_contact(self, contact: Dict[str, any]) -> Dict[str, any]:
        """Clean and standardize contact data before saving"""
        cleaned = {}
        for key, value in contact.items():
            if value is None:
                continue
            if isinstance(value, str):
                value = value.strip()
                if not value:
                    continue
            cleaned[key] = value
        return cleaned

    def save_contacts(self, email_account: str, contacts: List[Dict[str, any]]) -> None: 
        try:
            # Clean and filter contacts
            cleaned_contacts = []
            for contact in contacts:
                cleaned = self._clean_contact(contact)
                if cleaned.get('email') or cleaned.get('phone') or cleaned.get('linkedin'):
                    cleaned_contacts.append(cleaned)

            if not cleaned_contacts:
                logger.info("No valid contacts to save after cleaning")
                return

            # Clean filename
            safe_email = email_account.replace('@', '_at_').replace('.', '_')
            filename = f"{safe_email}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            file_path = os.path.join(self.output_dir, filename)

            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(cleaned_contacts, f, ensure_ascii=False, indent=2)

            logger.info(f"Saved {len(cleaned_contacts)} contacts to {file_path}")
        except Exception as e:
            logger.error(f"Failed to save contacts: {str(e)}")