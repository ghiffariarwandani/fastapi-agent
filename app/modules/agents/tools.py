from pathlib import Path

from agents import function_tool
from ddgs import DDGS

from app.core.settings import settings


@function_tool
def search_web(query: str):
    """
    Search the web for information using DDGS.

    query: The search query to use.
    label: The label to use to tell what you are currently doing with this tool
    """

    with DDGS() as ddgs:
        results = list(ddgs.text(query, max_results=3))
        print(results)

        return results

@function_tool
def read_uploaded_file(file_path: str) -> str:
    base_dir = Path(settings.UPLOAD_DIR).resolve()
    target = Path(file_path).resolve()

    if not str(target).startswith(str(base_dir)):
        return "Access denied."

    if not target.exists():
        return "File not found."

    if not target.is_file():
        return "Invalid file."

    try:
        return target.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return "File is not a readable text file."
    except Exception as e:
        return f"Failed to read file: {e}"
