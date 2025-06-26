
import yaml
import logging
import os
from datetime import datetime
from typing import List, Dict, Tuple
from mail_client import EmailClient  # Updated import
from extractor import ContactExtractor
from filters import EmailFilter
from storage import StorageManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(f'email_processor_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log')
    ]
)
logger = logging.getLogger("main")

class EmailProcessor:
    def __init__(self):
        self.stats = {
            'accounts_processed': 0,
            'total_emails_fetched': 0,
            'total_recruiter_emails': 0,
            'total_contacts_extracted': 0,
            'start_time': datetime.now(),
            'account_details': []
        }

    def load_accounts(self, filter_tags: List[str] = None) -> List[Dict]:
        """Load email accounts from configuration"""
        try:
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            accounts_path = os.path.join(base_dir, 'config', 'accounts.yaml')
            logger.debug(f"Loading accounts from: {accounts_path}")

            if not os.path.exists(accounts_path):
                logger.error(f"accounts.yaml not found at: {accounts_path}")
                return []

            with open(accounts_path, 'r') as file:
                config_data = yaml.safe_load(file)

            if not config_data or 'accounts' not in config_data:
                logger.error("Invalid accounts.yaml format. Missing 'accounts' key.")
                return []

            all_accounts = config_data['accounts']
            return [
                acc for acc in all_accounts
                if acc.get('active', True) and
                (not filter_tags or any(tag in acc.get('tags', []) for tag in filter_tags))
            ]
        except Exception as e:
            logger.error(f"Error loading accounts: {str(e)}")
            return []

    def process_account(self, account: Dict, extractor: ContactExtractor, email_filter: EmailFilter) -> Dict:
        """Process a single email account"""
        account_stats = {
            'email': account['email'],
            'emails_fetched': 0,
            'recruiter_emails': 0,
            'contacts_extracted': 0,
            'error': None,
            'total_in_mailbox': 0
        }

        try:
            logger.info(f"\n{'='*50}\nProcessing account: {account['email']}\n{'='*50}")

            # Initialize clients
            email_client = EmailClient(account)
            storage = StorageManager()

            if not email_client.connect():
                raise ConnectionError(f"Failed to connect to {account['email']}")

            # Fetch emails
            emails, total_in_mailbox = email_client.fetch_emails(
                limit=account.get('fetch_limit', 50),
                mark_as_read=account.get('mark_as_read', False)
            )
            account_stats['emails_fetched'] = len(emails)
            account_stats['total_in_mailbox'] = total_in_mailbox
            self.stats['total_emails_fetched'] += len(emails)

            if not emails:
                logger.info("No emails fetched from this account")
                return account_stats

            # Filter recruiter emails
            recruiter_emails = email_filter.filter_recruiter_emails(emails, extractor)
            account_stats['recruiter_emails'] = len(recruiter_emails)
            self.stats['total_recruiter_emails'] += len(recruiter_emails)
            logger.info(f"Found {len(recruiter_emails)} recruiter emails")

            # Extract contacts
            contacts = []
            for email_data in recruiter_emails:
                try:
                    contact = extractor.extract_contacts(
                        email_data['message'], 
                        source_email=account['email']
                    )
                    if contact.get('email'):
                        contacts.append(contact)
                except Exception as e:
                    logger.error(f"Error extracting contact: {str(e)}")
                    continue

            account_stats['contacts_extracted'] = len(contacts)
            self.stats['total_contacts_extracted'] += len(contacts)

            # Save contacts
            if contacts:
                storage.save_contacts(account['email'], contacts)
                logger.info(f"Saved {len(contacts)} contacts to storage")

            return account_stats

        except Exception as e:
            logger.error(f"Error processing account {account['email']}: {str(e)}")
            account_stats['error'] = str(e)
            return account_stats
        finally:
            email_client.disconnect()
            self.stats['account_details'].append(account_stats)
            self.stats['accounts_processed'] += 1

    def print_summary(self):
        """Print detailed processing summary"""
        duration = datetime.now() - self.stats['start_time']
        success_rate = (self.stats['total_contacts_extracted'] / self.stats['total_recruiter_emails'] * 100 
                       if self.stats['total_recruiter_emails'] > 0 else 0)
        
        logger.info("\n" + "="*60)
        logger.info(" PROCESSING SUMMARY ".center(60, "="))
        logger.info("="*60)
        
        # Overall stats
        logger.info(f"\nTotal processing time: {duration}")
        logger.info(f"Accounts processed: {self.stats['accounts_processed']}")
        logger.info(f"Total emails in mailboxes: {sum(acc.get('total_in_mailbox', 0) for acc in self.stats['account_details'])}")
        logger.info(f"Total emails fetched: {self.stats['total_emails_fetched']}")
        logger.info(f"Total recruiter emails found: {self.stats['total_recruiter_emails']}")
        logger.info(f"Total contacts extracted: {self.stats['total_contacts_extracted']}")
        logger.info(f"Success rate: {success_rate:.2f}%")
        
        # Per-account details
        logger.info("\nAccount Details:")
        for acc in self.stats['account_details']:
            logger.info(f"\nAccount: {acc['email']}")
            logger.info(f"- Emails in mailbox: {acc.get('total_in_mailbox', 'N/A')}")
            logger.info(f"- Emails fetched: {acc['emails_fetched']}")
            logger.info(f"- Recruiter emails: {acc['recruiter_emails']}")
            logger.info(f"- Contacts extracted: {acc['contacts_extracted']}")
            if acc['error']:
                logger.error(f"- ERROR: {acc['error']}")

def main():
    """Main execution function"""
    logger.info("Starting email contact extraction")
    
    processor = EmailProcessor()
    extractor = ContactExtractor()
    email_filter = EmailFilter()
    
    # Load and process accounts
    accounts = processor.load_accounts(filter_tags=["job_search"])
    if not accounts:
        logger.error("No active accounts found matching criteria")
        return
    
    for account in accounts:
        processor.process_account(account, extractor, email_filter)
    
    # Print final summary
    processor.print_summary()
    logger.info("Email contact extraction completed")

if __name__ == "__main__":
    main()