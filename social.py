"""For businesses WITHOUT a website: look for public social pages via web search."""
from duckduckgo_search import DDGS

def find_social(name: str, city: str) -> dict:
    found = {}
    try:
        with DDGS() as d:
            for key, dom in [("facebook", "facebook.com"), ("instagram", "instagram.com")]:
                for r in d.text(f"{name} {city} site:{dom}", max_results=2):
                    found[key] = r["href"]
                    break
    except Exception:
        pass
    return found
