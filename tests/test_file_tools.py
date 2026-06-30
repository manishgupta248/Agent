from tools.file_tools import read_csv_summary, write_text_file, read_text_file

def test_tools():
    print(read_csv_summary("sample.csv"))
    print(write_text_file("note.txt", "Hello from the agent."))
    print(read_text_file("note.txt"))

if __name__ == "__main__":
    test_tools()