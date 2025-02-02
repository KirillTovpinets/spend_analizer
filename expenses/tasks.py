import imaplib
import email
from email.header import decode_header
import os

# Yahoo Mail IMAP settings
IMAP_SERVER = "imap.mail.yahoo.com"
IMAP_PORT = 993

# Your Yahoo Mail credentials
username = "your_yahoo_email@yahoo.com"
password = "your_app_password"  # Use the app password generated from Yahoo

# Create a connection to Yahoo Mail
mail = imaplib.IMAP4_SSL(IMAP_SERVER, IMAP_PORT)

# Log in to the account
mail.login(username, password)

# Select the mailbox you want to search (inbox by default)
mail.select("inbox")

# Search for emails with "receipt", "invoice", or "purchase" in the subject
status, messages = mail.search(None, '(SUBJECT "receipt" SUBJECT "invoice" SUBJECT "purchase")')

# Get the list of email IDs
email_ids = messages[0].split()

# Create a folder to store the receipts if it doesn't exist
if not os.path.exists('receipts'):
    os.makedirs('receipts')

# Loop through the list of emails
for email_id in email_ids:
    # Fetch the email by ID
    status, data = mail.fetch(email_id, "(RFC822)")

    # Iterate through the responses
    for response in data:
        if isinstance(response, tuple):
            # Parse the raw email bytes to an email message object
            msg = email.message_from_bytes(response[1])

            # Decode the email subject
            subject, encoding = decode_header(msg["Subject"])[0]
            if isinstance(subject, bytes):
                # Convert the subject to a string if it's bytes
                subject = subject.decode(encoding if encoding else 'utf-8')

            print("Subject:", subject)

            # If the email message is multipart
            if msg.is_multipart():
                # Walk through the parts of the email
                for part in msg.walk():
                    # If part is an attachment
                    if part.get_content_maintype() == 'multipart':
                        continue
                    if part.get("Content-Disposition") is None:
                        continue

                    # Get the filename of the attachment
                    filename = part.get_filename()
                    if filename:
                        # Save the attachment
                        filepath = os.path.join("receipts", filename)
                        with open(filepath, "wb") as f:
                            f.write(part.get_payload(decode=True))
                        print(f"Saved receipt to {filepath}")
            else:
                # If the message is not multipart, save the text payload
                content_type = msg.get_content_type()
                if content_type == "text/plain":
                    # Save the plain text part
                    filepath = os.path.join("receipts", f"{subject}.txt")
                    with open(filepath, "w") as f:
                        f.write(msg.get_payload(decode=True).decode('utf-8'))
                    print(f"Saved text receipt to {filepath}")

# Logout from the server
mail.logout()
