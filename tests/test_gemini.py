from google import genai
from config.settings import GEMINI_API_KEY


def test_gemini():
    print("\n=== Testing Gemini API ===")
    try:
        client = genai.Client(api_key=GEMINI_API_KEY)

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents="Reply with exactly one word: OK"
        )

        print("\nSUCCESS\n")
        print(response.text)

    except Exception as e:
        print("\nFAILED\n")
        print(e)


if __name__ == "__main__":
    test_gemini()