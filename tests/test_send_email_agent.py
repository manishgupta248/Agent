from agents.file_agent_graph import run_agent_with_history

def test():
    answer, _ = run_agent_with_history(
        "Send an email to manish248gupta@gmail.com with subject 'Hello from Agent' "
        "and body 'Your AI agent is working perfectly.'",
        history=[]
    )
    print(answer)

if __name__ == "__main__":
    test()