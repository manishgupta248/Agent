from agents.file_agent_graph import build_file_agent_graph

def test_graph():
    app = build_file_agent_graph()
    result = app.invoke(
        {"messages": [{"role": "user", "content": "How many rows and columns are in sample.csv?"}]}
    )
    print("\n--- Final Answer ---")
    print(result["messages"][-1]["content"])

if __name__ == "__main__":
    test_graph()