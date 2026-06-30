from agents.file_agent import run_file_agent

def test_agent():
    answer = run_file_agent("How many rows and columns are in sample.csv, and what are the column names?, cteate a text file and update it with answer")
    print("\n--- Final Answer ---")
    print(answer)

if __name__ == "__main__":
    test_agent()