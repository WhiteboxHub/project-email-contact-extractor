import logging
import os
import json
from datetime import datetime
import mysql.connector
from dotenv import load_dotenv

load_dotenv()  

class StorageManager:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.data_dir = os.path.join(base_dir, 'data')
        self.last_run_path = os.path.join(self.data_dir, 'last_run.json')
        os.makedirs(self.data_dir, exist_ok=True)

        self.db_config = {
            'host': os.getenv('DB_HOST', 'localhost'),
            'user': os.getenv('DB_USER', 'root'),
            'password': os.getenv('DB_PASSWORD', ''),
            'database': os.getenv('DB_NAME', 'your_database')
        }

    def save_contacts(self, email_account: str, contacts: list):
        if not contacts:
            self.logger.info(f"No contacts to save for {email_account}")
            return

        try:
            conn = mysql.connector.connect(**self.db_config)
            cursor = conn.cursor()

            insert_query = """
                INSERT INTO vendor_contact_extracts (
                    full_name, source_email, email, phone,
                    linkedin_id, company_name, location,
                    extraction_date, moved_to_vendor, created_at
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, CURDATE(), 0, NOW())
                ON DUPLICATE KEY UPDATE
                    phone=VALUES(phone), company_name=VALUES(company_name),
                    linkedin_id=VALUES(linkedin_id), location=VALUES(location),
                    moved_to_vendor=VALUES(moved_to_vendor)
            """

            new_count = 0
            for contact in contacts:
                if not contact.get('email'):
                    continue

                values = (
                    contact.get('name', ''),
                    contact.get('source', email_account).lower(),
                    contact.get('email'),
                    contact.get('phone', ''),
                    contact.get('linkedin_id', ''),
                    contact.get('company', ''),
                    contact.get('location', ''),
                )
                cursor.execute(insert_query, values)
                new_count += 1

            conn.commit()
            cursor.close()
            conn.close()

            self.logger.info(f"Inserted {new_count} contacts into database.")

        except mysql.connector.Error as err:
            self.logger.error(f"MySQL error: {err}")
        except Exception as e:
            self.logger.error(f"Unexpected error saving contacts: {str(e)}")

    def load_last_run(self):
        try:
            if os.path.exists(self.last_run_path):
                with open(self.last_run_path, 'r') as f:
                    return json.load(f)
            return {}
        except Exception as e:
            self.logger.error(f"Error loading last run data: {str(e)}")
            return {}

    def save_last_run(self, email_account: str, last_uid: str):
        try:
            data = self.load_last_run()
            data[email_account] = {
                'last_uid': last_uid,
                'last_run': datetime.now().isoformat()
            }

            with open(self.last_run_path, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            self.logger.error(f"Error saving last run data: {str(e)}")