from config.google.auth import get_google_credentials

def test_auth():
    print("\n=== Testing Google OAuth ===")
    creds = get_google_credentials()
    print("\nSUCCESS — credentials obtained.")
    print(f"Token valid: {creds.valid}")
    print(f"Scopes granted: {creds.scopes}")

if __name__ == "__main__":
    test_auth()