from agents import function_tool
from ddgs import DDGS


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
