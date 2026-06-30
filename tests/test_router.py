from core.llm_router import get_llm_response

def test_router():
    messages = [{"role": "user", "content": "Reply with exactly one word: PONG"}]
    result = get_llm_response(messages)
    print("\n--- Router Result ---")
    print(f"Provider used: {result['provider']}")
    print(f"Content: {result['content']}")

if __name__ == "__main__":
    test_router()