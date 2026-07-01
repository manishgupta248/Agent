import base64
from googleapiclient.discovery import build
import email.mime.text
import email.mime.multipart
import base64
from config.google.auth import get_google_credentials


def _get_gmail_service():
    creds = get_google_credentials()
    return build("gmail", "v1", credentials=creds)


def fetch_unread_emails(max_results: int = 5) -> str:
    """
    Fetches the most recent unread emails from the inbox.
    Returns a summary string: sender, subject, and a short snippet for each.
    """
    service = _get_gmail_service()

    results = (
        service.users()
        .messages()
        .list(userId="me", labelIds=["INBOX", "UNREAD"], maxResults=max_results)
        .execute()
    )
    messages = results.get("messages", [])

    if not messages:
        return "No unread emails found."

    summaries = []
    for msg_ref in messages:
        msg = (
            service.users()
            .messages()
            .get(userId="me", id=msg_ref["id"], format="metadata",
                 metadataHeaders=["From", "Subject"])
            .execute()
        )
        headers = {h["name"]: h["value"] for h in msg["payload"]["headers"]}
        sender = headers.get("From", "Unknown sender")
        subject = headers.get("Subject", "(no subject)")
        snippet = msg.get("snippet", "")

        summaries.append(f"From: {sender}\nSubject: {subject}\nSnippet: {snippet}")

    return "\n---\n".join(summaries)



def send_email(to: str, subject: str, body: str) -> str:
    """
    Sends an email from your Gmail account.
    to: recipient email address
    subject: email subject line
    body: plain text email body
    """
    service = _get_gmail_service()

    message = email.mime.multipart.MIMEMultipart()
    message["to"] = to
    message["subject"] = subject
    message.attach(email.mime.text.MIMEText(body, "plain"))

    raw = base64.urlsafe_b64encode(message.as_bytes()).decode()

    sent = (
        service.users()
        .messages()
        .send(userId="me", body={"raw": raw})
        .execute()
    )

    return f"Email sent successfully. Message ID: {sent['id']}"