"""AI layer: score each lead for agency fit and draft a first-line pitch (Gemini free tier)."""
import json, re
from google import genai
import config

def analyze(lead: dict) -> dict:
    key = config.get("GEMINI_API_KEY")
    if not key:
        return {}
    client = genai.Client(api_key=key)
    prompt = f"""You qualify leads for a digital agency selling: websites, web apps, mobile apps,
branding/creative, AI automation & workflows.
Business: {lead.get('name')} | Category: {lead.get('category')} | City: {lead.get('city')}
Website: {lead.get('website') or 'NONE'} | Facebook: {lead.get('facebook') or 'none'} | Instagram: {lead.get('instagram') or 'none'}
Website text sample: {str(lead.get('site_text', ''))[:800]}
Return ONLY JSON: {{"score": 1-10, "best_service": "...", "reason": "one sentence",
"pitch": "2 sentence friendly personalised opener, no hype"}}"""
    try:
        r = client.models.generate_content(model=config.get("GEMINI_MODEL", "gemini-2.5-flash"),
                                           contents=prompt)
        data = json.loads(re.search(r"\{.*\}", r.text, re.S).group())
        return {"ai_score": data.get("score"), "best_service": data.get("best_service"),
                "ai_reason": data.get("reason"), "pitch": data.get("pitch")}
    except Exception:
        return {}
