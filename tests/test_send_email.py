from tools.gmail_tools import send_email

def test_send():
    result = send_email(
        to="manish248gupta@gmail.com",  # sending to yourself for test
        subject="Agent Test Email",
        body="This email was sent autonomously by your local AI agent. Feature 1 working correctly."
    )
    print(result)

if __name__ == "__main__":
    test_send()