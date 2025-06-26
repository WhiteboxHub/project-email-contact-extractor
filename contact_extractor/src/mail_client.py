
import imaplib
import email
from email.header import decode_header
import logging
from typing import Dict, List, Tuple, Optional, Any

logger = logging.getLogger("mail_client")

class EmailClient:
    def __init__(self, account: Dict):
        self.account = account
        self.conn = None
        self.total_emails_in_mailbox = 0
        self.processed_emails_count = 0

    def connect(self) -> bool:
        """Connect to IMAP server and login"""
        try:
            logger.info(f"Connecting to {self.account['imap_server']}...")
            self.conn = imaplib.IMAP4_SSL(
                self.account['imap_server'], 
                self.account['imap_port']
            )
            self.conn.login(
                self.account['email'], 
                self.account['password']
            )
            logger.info("Successfully connected to IMAP server")
            return True
        except imaplib.IMAP4.error as e:
            logger.error(f"IMAP login failed: {str(e)}")
            return False
        except Exception as e:
            logger.error(f"Connection error: {str(e)}")
            return False

    def fetch_emails(
        self, 
        mailbox: str = "INBOX", 
        limit: int = 50,
        mark_as_read: bool = False
    ) -> Tuple[List[Dict], int]:
        """
        Fetch emails from the specified mailbox
        
        Args:
            mailbox: Mailbox to fetch from (default: INBOX)
            limit: Maximum number of emails to fetch (default: 50)
            mark_as_read: Whether to mark fetched emails as read (default: False)
            
        Returns:
            Tuple of (list of email dicts, total emails in mailbox)
        """
        try:
            # Select mailbox and get total message count
            status, [message_ids] = self.conn.select(mailbox)
            self.total_emails_in_mailbox = int(message_ids)
            logger.info(f"Total emails in {mailbox}: {self.total_emails_in_mailbox}")

            if self.total_emails_in_mailbox == 0:
                logger.info("No emails to fetch")
                return [], 0

            # Determine range of emails to fetch (most recent first)
            end = self.total_emails_in_mailbox
            start = max(1, end - limit + 1)
            self.processed_emails_count = end - start + 1
            logger.info(f"Fetching {self.processed_emails_count} emails (limit: {limit})")

            # Fetch emails
            emails = []
            for i in range(start, end + 1):
                try:
                    res, msg_data = self.conn.fetch(str(i), "(RFC822)")
                    if res != 'OK' or not msg_data:
                        continue

                    raw_email = msg_data[0][1]
                    # Correct way to parse email from bytes
                    msg = email.message_from_bytes(raw_email)
                    parsed_email = self._parse_email(msg)
                    emails.append({
                        "id": str(i),
                        "message": parsed_email
                    })

                    if mark_as_read:
                        self.conn.store(str(i), '+FLAGS', '\Seen')

                except Exception as e:
                    logger.error(f"Error processing email {i}: {str(e)}")
                    continue

            logger.info(f"Successfully fetched {len(emails)} emails")
            return emails, self.total_emails_in_mailbox

        except Exception as e:
            logger.error(f"Failed to fetch emails: {str(e)}")
            return [], 0

    def _parse_email(self, msg) -> Dict:
        """Parse email message into structured data"""
        # Initialize with default values
        email_data = {
            "from": "",
            "to": "",
            "subject": "",
            "body": "",
            "date": "",
            "cc": "",
            "headers": {}
        }

        # Decode headers
        for header in ['From', 'To', 'Subject', 'Date', 'Cc']:
            value = msg.get(header, "")
            email_data[header.lower()] = self._decode_header(value)

        # Store all headers
        for header, value in msg.items():
            email_data['headers'][header] = self._decode_header(value)

        # Extract body content
        email_data['body'] = self._extract_body(msg)

        return email_data

    def _decode_header(self, header: str) -> str:
        """Decode email headers"""
        if not header:
            return ""

        try:
            decoded_parts = decode_header(header)
            decoded_str = []
            for part, encoding in decoded_parts:
                if isinstance(part, bytes):
                    try:
                        decoded_str.append(part.decode(encoding or 'utf-8', errors='replace'))
                    except (UnicodeDecodeError, LookupError):
                        decoded_str.append(part.decode('utf-8', errors='replace'))
                else:
                    decoded_str.append(str(part))
            return ''.join(decoded_str)
        except Exception as e:
            logger.warning(f"Failed to decode header: {str(e)}")
            return str(header)

    def _extract_body(self, msg) -> str:
        """Extract text body from email message"""
        body = ""
        if msg.is_multipart():
            for part in msg.walk():
                content_type = part.get_content_type()
                content_disposition = str(part.get("Content-Disposition"))

                # Skip attachments
                if 'attachment' in content_disposition:
                    continue

                # Prefer text/plain over text/html
                if content_type == "text/plain":
                    charset = part.get_content_charset() or 'utf-8'
                    try:
                        body = part.get_payload(decode=True).decode(charset, errors='replace')
                        break  # Prefer plain text
                    except Exception as e:
                        logger.warning(f"Failed to decode plain text body: {str(e)}")
                elif content_type == "text/html" and not body:
                    charset = part.get_content_charset() or 'utf-8'
                    try:
                        body = part.get_payload(decode=True).decode(charset, errors='replace')
                    except Exception as e:
                        logger.warning(f"Failed to decode HTML body: {str(e)}")
        else:
            charset = msg.get_content_charset() or 'utf-8'
            try:
                body = msg.get_payload(decode=True).decode(charset, errors='replace')
            except Exception as e:
                logger.warning(f"Failed to decode simple body: {str(e)}")

        # Clean up the body text
        if body:
            body = body.strip()
            # Remove excessive whitespace and line breaks
            body = ' '.join(body.split())
        return body

    def disconnect(self):
        """Close IMAP connection"""
        try:
            if self.conn:
                logger.info("Closing IMAP connection...")
                self.conn.logout()
                logger.info("Disconnected successfully")
        except Exception as e:
            logger.warning(f"Error during disconnect: {str(e)}")
        finally:
            self.conn = None