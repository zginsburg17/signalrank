import requests
from app.core.config import settings


class EnrichmentService:
    def analyze_text(self, text: str) -> dict:
        payload = {"text": text}
        headers = {
            "Authorization": f"Bearer {settings.enrichment_api_key}",
            "Content-Type": "application/json",
        }

        # Placeholder for a real provider call.
        # Replace this block with your actual external API integration.
        if settings.enrichment_api_url.startswith("https://example.com"):
            lowered = text.lower()
            sentiment = "negative" if any(word in lowered for word in ["confusing", "failed", "slow", "charged", "error"]) else "neutral"
            if "bill" in lowered or "charged" in lowered or "payment" in lowered:
                issue = "billing"
            elif "support" in lowered or "respond" in lowered:
                issue = "support"
            elif "onboarding" in lowered:
                issue = "onboarding"
            elif "pricing" in lowered:
                issue = "pricing"
            else:
                issue = "other"
            return {"sentiment": sentiment, "issue_label": issue, "provider": "mock"}

        response = requests.post(
            settings.enrichment_api_url,
            json=payload,
            headers=headers,
            timeout=settings.request_timeout_seconds,
        )
        response.raise_for_status()
        return response.json()
