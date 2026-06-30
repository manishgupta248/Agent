from agents.file_agent_graph import build_file_agent_graph

def test_gmail_agent():
    app = build_file_agent_graph()
    result = app.invoke(
        {"messages": [{"role": "user", "content": "Check my unread emails and summarize them for me."}]}
    )
    print("\n--- Final Answer ---")
    print(result["messages"][-1]["content"])

if __name__ == "__main__":
    test_gmail_agent()