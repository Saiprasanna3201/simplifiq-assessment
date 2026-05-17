import os
import re
import requests
from bs4 import BeautifulSoup
from anthropic import Anthropic

client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )
}


def scrape_website(url):
    """Scrape raw text from the company's website."""
    if not url.startswith("http"):
        url = "https://" + url
    try:
        resp = requests.get(url, headers=HEADERS, timeout=10)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")

        # Remove nav/footer noise
        for tag in soup(["script", "style", "nav", "footer", "header"]):
            tag.decompose()

        text = soup.get_text(separator=" ", strip=True)
        # Collapse whitespace
        text = re.sub(r"\s+", " ", text)
        return text[:4000]  # cap to avoid token overflow

    except Exception as e:
        print(f"  [scraper] Website scrape failed: {e}")
        return ""


def scrape_linkedin_hint(company_name):
    """Try to get a LinkedIn description via Google search snippet."""
    query = f"{company_name} company LinkedIn about"
    try:
        resp = requests.get(
            "https://www.google.com/search",
            params={"q": query},
            headers=HEADERS,
            timeout=8,
        )
        soup = BeautifulSoup(resp.text, "html.parser")
        snippets = soup.select("div.BNeawe")
        texts = [s.get_text() for s in snippets[:5]]
        return " ".join(texts)[:1500]
    except Exception as e:
        print(f"  [scraper] LinkedIn hint failed: {e}")
        return ""


def enrich_with_claude(lead, website_text, linkedin_text):
    """Use Claude to synthesize scraped data into structured company insights."""

    prompt = f"""You are a business research analyst. Based on the information below, generate a detailed company audit/profile.

LEAD INFORMATION:
- Name: {lead['name']}
- Role: {lead.get('role', 'Not specified')}
- Company: {lead['company']}
- Website: {lead['website']}
- Industry: {lead['industry']}
- Message: {lead.get('message', 'None')}

SCRAPED WEBSITE CONTENT:
{website_text or 'Not available'}

ADDITIONAL CONTEXT:
{linkedin_text or 'Not available'}

Generate a JSON object with these exact keys:
{{
  "company_overview": "2-3 sentence overview of what the company does",
  "industry_segment": "specific segment within their industry",
  "key_services": ["service1", "service2", "service3"],
  "target_market": "who they serve",
  "company_size_estimate": "startup/SME/mid-market/enterprise",
  "pain_points": ["likely business challenge 1", "challenge 2", "challenge 3"],
  "opportunities": ["how SimplifIQ could help them 1", "opportunity 2", "opportunity 3"],
  "digital_maturity": "low/medium/high — based on their web presence",
  "personalized_intro": "A warm, specific 2-sentence opening for the email/report that references their actual work",
  "recommended_solutions": ["specific SimplifIQ solution recommendation 1", "recommendation 2"],
  "competitive_landscape": "brief note on what competitors they likely face",
  "key_insight": "One sharp, impressive insight about their business that shows deep research"
}}

Return ONLY valid JSON, no markdown, no explanation."""

    try:
        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1500,
            messages=[{"role": "user", "content": prompt}],
        )
        raw = response.content[0].text.strip()
        # Strip markdown fences if present
        raw = re.sub(r"^```json\s*|```$", "", raw, flags=re.MULTILINE).strip()
        import json
        return json.loads(raw)
    except Exception as e:
        print(f"  [claude] Enrichment failed: {e}")
        return _fallback_enrichment(lead)


def _fallback_enrichment(lead):
    """Graceful fallback if Claude or scraping fails."""
    return {
        "company_overview": f"{lead['company']} is a company in the {lead['industry']} industry.",
        "industry_segment": lead["industry"],
        "key_services": ["Core service 1", "Core service 2", "Core service 3"],
        "target_market": "Business customers",
        "company_size_estimate": "SME",
        "pain_points": [
            "Manual process inefficiencies",
            "Lead follow-up delays",
            "Lack of automation",
        ],
        "opportunities": [
            "Automate lead intake workflows",
            "Streamline client onboarding",
            "Reduce manual data entry",
        ],
        "digital_maturity": "medium",
        "personalized_intro": (
            f"Thank you for your interest, {lead['name']}. "
            f"We've prepared a custom audit for {lead['company']}."
        ),
        "recommended_solutions": [
            "Workflow automation suite",
            "AI-powered lead management",
        ],
        "competitive_landscape": "Competitive market with opportunities for differentiation through automation.",
        "key_insight": f"{lead['company']} stands to gain significant efficiency through targeted automation.",
    }


def enrich_company(lead):
    """Main enrichment entry point — scrape + Claude analysis."""
    print(f"  Scraping website: {lead['website']}")
    website_text = scrape_website(lead["website"])

    print(f"  Fetching LinkedIn hints for: {lead['company']}")
    linkedin_text = scrape_linkedin_hint(lead["company"])

    print(f"  Running Claude analysis...")
    enriched = enrich_with_claude(lead, website_text, linkedin_text)

    return enriched
