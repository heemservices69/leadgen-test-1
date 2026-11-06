"""Enrichment: pull public contact info from a business's own website (robots.txt respected)."""
import re, requests
from urllib.parse import urljoin, urlparse
from urllib.robotparser import RobotFileParser
from bs4 import BeautifulSoup
from config import USER_AGENT

EMAIL = re.compile(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}")
BAD_EXT = (".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg")
SOCIAL = {"facebook": "facebook.com", "instagram": "instagram.com",
          "linkedin": "linkedin.com", "twitter": "x.com"}

def _allowed(url):
    try:
        p = urlparse(url)
        rp = RobotFileParser(f"{p.scheme}://{p.netloc}/robots.txt")
        rp.read()
        return rp.can_fetch(USER_AGENT, url)
    except Exception:
        return True

def _get(url):
    if not _allowed(url):
        return ""
    try:
        r = requests.get(url, headers={"User-Agent": USER_AGENT}, timeout=10)
        return r.text if r.ok else ""
    except Exception:
        return ""

def scrape(website: str) -> dict:
    if not website:
        return {}
    if not website.startswith("http"):
        website = "https://" + website
    emails, phones, social, text = set(), set(), {}, ""
    for path in ["", "/contact", "/contact-us", "/about"]:
        html = _get(urljoin(website, path))
        if not html:
            continue
        soup = BeautifulSoup(html, "html.parser")
        for a in soup.select("a[href]"):
            h = a["href"]
            if h.startswith("mailto:"):
                emails.add(h[7:].split("?")[0].lower())
            if h.startswith("tel:"):
                phones.add(h[4:].strip())
            for k, dom in SOCIAL.items():
                if dom in h and k not in social:
                    social[k] = h
        text += soup.get_text(" ", strip=True)[:1500] + " "
        emails |= {e.lower() for e in EMAIL.findall(html) if not e.lower().endswith(BAD_EXT)}
    return {"email": ", ".join(sorted(emails)[:3]), "phone": ", ".join(sorted(phones)[:2]),
            "site_text": text[:2500], **social}
