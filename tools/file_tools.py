import os
import pandas as pd

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")


def _safe_path(filename: str) -> str:
    """Restrict all file operations to the data/ folder."""
    path = os.path.abspath(os.path.join(DATA_DIR, filename))
    if not path.startswith(os.path.abspath(DATA_DIR)):
        raise ValueError("Access outside data/ directory is not allowed.")
    return path


def read_text_file(filename: str) -> str:
    path = _safe_path(filename)
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def write_text_file(filename: str, content: str) -> str:
    path = _safe_path(filename)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    return f"Written {len(content)} characters to {filename}"


def read_csv_summary(filename: str) -> str:
    path = _safe_path(filename)
    df = pd.read_csv(path)
    return (
        f"Rows: {len(df)}, Columns: {list(df.columns)}\n"
        f"First 5 rows:\n{df.head().to_string()}"
    )


def read_excel_summary(filename: str, sheet_name: str = 0) -> str:
    path = _safe_path(filename)
    df = pd.read_excel(path, sheet_name=sheet_name)
    return (
        f"Rows: {len(df)}, Columns: {list(df.columns)}\n"
        f"First 5 rows:\n{df.head().to_string()}"
    )