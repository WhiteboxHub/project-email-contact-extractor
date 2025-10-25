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
            cursor = conn.cursor(dictionary=True)
            new_count = 0

            for contact in contacts:
                email = contact.get('email')
                linkedin = contact.get('linkedin_id')
                name = contact.get('name', '')
                phone = contact.get('phone', '')
                company = contact.get('company', '')
                location = contact.get('location', '')
                source = contact.get('source', email_account).lower()

                if email:
                    cursor.execute("SELECT * FROM vendor_contact_extracts WHERE email = %s", (email,))
                    row = cursor.fetchone()
                    if row:
                        if not row["linkedin_id"] and linkedin:
                            cursor.execute("""
                                UPDATE vendor_contact_extracts
                                SET linkedin_id=%s, full_name=%s, phone=%s,
                                    company_name=%s, location=%s, source_email=%s
                                WHERE id=%s
                            """, (linkedin, name, phone, company, location, source, row["id"]))
                            conn.commit()
                        continue

                if linkedin:
                    cursor.execute("SELECT * FROM vendor_contact_extracts WHERE linkedin_id = %s", (linkedin,))
                    row = cursor.fetchone()
                    if row:
                        if not row["email"] and email:
                            cursor.execute("""
                                UPDATE vendor_contact_extracts
                                SET email=%s, full_name=%s, phone=%s,
                                    company_name=%s, location=%s, source_email=%s
                                WHERE id=%s
                            """, (email, name, phone, company, location, source, row["id"]))
                            conn.commit()
                        continue

                cursor.execute("""
                    INSERT INTO vendor_contact_extracts
                    (full_name, source_email, email, phone, linkedin_id, company_name, location, extraction_date, moved_to_vendor, created_at)
                    VALUES (%s,%s,%s,%s,%s,%s,%s,CURDATE(),0,NOW())
                """, (name, source, email, phone, linkedin, company, location))
                conn.commit()
                new_count += 1

            cursor.close()
            conn.close()
            self.logger.info(f"Inserted {new_count} new contacts into database.")

        except mysql.connector.Error as err:
            self.logger.error(f"MySQL error: {err}")
        except Exception as e:
            self.logger.error(f"Unexpected error saving contacts: {str(e)}")

    
    def log_email_activity(self, candidate_email, emails_count):
        """
        Logs the number of emails processed for a candidate.
        Inserts new row if doesn't exist, increments emails_read if exists.
        """
        try:
            conn = mysql.connector.connect(**self.db_config)
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO email_activity_log (candidate_marketing_id, email, emails_read, activity_date)
                SELECT id, %s, %s, CURDATE()
                FROM candidate_marketing
                WHERE email=%s
                ON DUPLICATE KEY UPDATE
                    emails_read = emails_read + VALUES(emails_read),
                    last_updated = CURRENT_TIMESTAMP
            """, (candidate_email, emails_count, candidate_email))
            conn.commit()
            cursor.close()
            conn.close()
            self.logger.info(f"Logged {emails_count} emails for {candidate_email} in email_activity_log")
        except Exception as e:
            self.logger.error(f"Failed to log email activity: {e}")
    
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

