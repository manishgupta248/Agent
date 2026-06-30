from agents.file_agent_graph import build_file_agent_graph

def test_full_chain():
    app = build_file_agent_graph()
    result = app.invoke(
        {
            "messages": [
                {
                    "role": "user",
                    "content": (
                        "Check my unread emails, write a short summary of them to a "
                        "file called email_summary.txt, then upload that file to Google Drive."
                    ),
                }
            ]
        },
        config={"recursion_limit": 15},
    )
    print("\n--- Final Answer ---")
    print(result["messages"][-1]["content"])

if __name__ == "__main__":
    test_full_chain()