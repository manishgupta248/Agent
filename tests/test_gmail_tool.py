from tools.gmail_tools import fetch_unread_emails

def test_gmail():
    print(fetch_unread_emails(max_results=3))

if __name__ == "__main__":
    test_gmail()