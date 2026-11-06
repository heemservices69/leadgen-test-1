# Agency Lead Finder
Discover businesses anywhere in the world (OpenStreetMap, 100% free) -> enrich contacts from their public website/social -> AI score + pitch (Gemini) -> Google Sheet.

Run locally: `pip install -r requirements.txt && streamlit run app.py`

Structure: sources/ (discovery) · enrich/ (website + social) · ai/ (Gemini) · sheets.py · pipeline.py · app.py

Use responsibly: only public business contact data, respect robots.txt, follow anti-spam/privacy law (GDPR, CAN-SPAM, PECA), include opt-out in outreach.
