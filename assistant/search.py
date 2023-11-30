import requests
from bs4 import BeautifulSoup
from langchain.utilities import DuckDuckGoSearchAPIWrapper

ddg_search = DuckDuckGoSearchAPIWrapper()

def web_search(query: str, num_results: int = 3):
    try:
        results = ddg_search.results(query, num_results)
        return [r['link'] for r in results]
    except Exception as e:
        return f"Error: {e}"
    
def scrap_text(url: str):
    try:
        page = requests.get(url)
        soup = BeautifulSoup(page.content, 'html.parser')
        
        # Extract all the text from the page
        text = soup.get_text(separator=' ', strip=True)
        return text
    
    except Exception as e:
        print(e)
        return f"Error: {e}"
    
def collapse_list_of_lists(list_of_lists):
    content = []
    for l in list_of_lists:
        content.append("\n\n".join(l))
    return "\n\n".join(content)