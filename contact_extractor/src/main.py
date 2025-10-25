import yaml
import logging
import os
from email_client import EmailClient
from extractor import NERContactExtractor
from filters import MLRecruiterFilter
from storage import StorageManager

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)

def load_accounts(filter_tags=None):
    try:
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        accounts_path = os.path.join(base_dir, 'config', 'accounts.yaml')
        logging.info(f"Loading accounts from: {accounts_path}")

        with open(accounts_path, 'r', encoding='utf-8-sig') as file:
            data = yaml.safe_load(file)

        if not data or 'accounts' not in data:
            logging.error("'accounts' key missing or YAML empty")
            return []

        all_accounts = data['accounts']
        filtered_accounts = [
            acc for acc in all_accounts
            if acc.get('active', True) and
            (not filter_tags or any(tag in acc.get('tags', []) for tag in filter_tags))
        ]
        logging.info(f"Filtered {len(filtered_accounts)} active accounts")
        return filtered_accounts

    except Exception as e:
        logging.error(f"Error loading accounts: {str(e)}")
        return []

def deduplicate_contacts(contacts):
    seen = set()
    unique_contacts = []
    for contact in contacts:
        key = (contact['email'].lower(), contact.get('company', '').lower())
        if key not in seen:
            seen.add(key)
            unique_contacts.append(contact)
    return unique_contacts

def process_account(account, storage, extractor, email_filter, batch_size=100):
    email_client = EmailClient(account)
    if not email_client.connect():
        logging.error(f"Failed to connect to {account['email']}")
        return

    try:
        last_run = storage.load_last_run()
        account_last_run = last_run.get(account['email'], {})
        last_uid = account_last_run.get('last_uid')

        start_index = 0
        max_uid_seen = int(last_uid) if last_uid else 0
        total_extracted = 0

        while True:
            emails, next_start_index = email_client.fetch_emails(
                since_uid=last_uid, batch_size=batch_size, start_index=start_index
            )
            if not emails:
                break

            recruiter_emails = email_filter.filter_recruiter_emails(emails, extractor)
            contacts = []
            for email_data in recruiter_emails:
                try:
                    contact = extractor.extract_contacts(email_data['message'], source_email=account['email'])
                    if contact.get('email'):
                        contacts.append(contact)
                except Exception as e:
                    logging.error(f"Error extracting contact: {e}")
                    continue

            contacts = deduplicate_contacts(contacts)
            if contacts:
                storage.save_contacts(account['email'], contacts)
                total_extracted += len(contacts)

            storage.log_email_activity(account['email'], len(recruiter_emails))

            batch_uids = [int(email['uid']) for email in emails if email.get('uid')]
            if batch_uids:
                max_uid_seen = max(max_uid_seen, max(batch_uids))
                storage.save_last_run(account['email'], str(max_uid_seen))

            if not next_start_index:
                break
            start_index = next_start_index

        logging.info(f"Completed processing for {account['email']}. Total contacts extracted: {total_extracted}")

    except Exception as e:
        logging.error(f"Error processing account {account['email']}: {e}")
    finally:
        email_client.disconnect()

def main():
    logging.info(" Starting email contact extraction...")
    accounts = load_accounts(filter_tags=["job_search"])
    if not accounts:
        logging.error("No active accounts found")
        return

    storage = StorageManager()
    extractor = NERContactExtractor()
    email_filter = MLRecruiterFilter(model_dir="../models")

    for account in accounts:
        logging.info(f"Processing account: {account['email']}")
        process_account(account, storage, extractor, email_filter)

    logging.info("Email contact extraction completed")

if __name__ == "__main__":
    main()


