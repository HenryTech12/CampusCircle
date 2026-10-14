from dataclasses import dataclass
import httpx
from .config import Settings


class ProviderUnavailable(RuntimeError):
    """A provider capability is unavailable; callers must fail safely."""


@dataclass
class EmailService:
    settings: Settings

    async def send(self, *, recipient: str, subject: str, html: str) -> str:
        if not self.settings.brevo_api_key or not self.settings.brevo_sender_email:
            raise ProviderUnavailable("Brevo email delivery is not configured")
        payload = {
            "sender": {"email": self.settings.brevo_sender_email, "name": self.settings.brevo_sender_name},
            "to": [{"email": recipient}],
            "subject": subject,
            "htmlContent": html,
        }
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.post(
                "https://api.brevo.com/v3/smtp/email",
                headers={"api-key": self.settings.brevo_api_key, "accept": "application/json"},
                json=payload,
            )
        if response.status_code >= 300:
            raise ProviderUnavailable(f"Brevo rejected email with HTTP {response.status_code}")
        return str(response.json().get("messageId", "accepted"))


@dataclass
class GroqService:
    settings: Settings

    async def answer(self, question: str, facts: dict) -> str:
        if not self.settings.groq_api_key or not self.settings.groq_model:
            return "Copilot is unavailable until the server administrator configures Groq."
        prompt = (
            "Answer briefly using only the authoritative facts below. Never make financial decisions "
            "or invent values. If a fact is missing, say so.\n"
            f"Facts: {facts}\nQuestion: {question}"
        )
        async with httpx.AsyncClient(timeout=20) as client:
            response = await client.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers={"Authorization": f"Bearer {self.settings.groq_api_key}"},
                json={"model": self.settings.groq_model, "messages": [{"role": "user", "content": prompt}], "temperature": 0},
            )
        if response.status_code >= 300:
            raise ProviderUnavailable(f"Groq rejected request with HTTP {response.status_code}")
        return response.json()["choices"][0]["message"]["content"]


@dataclass
class BmoniService:
    settings: Settings

    def require_configured(self) -> None:
        if not self.settings.bmoni_api_key or not self.settings.bmoni_base_url:
            raise ProviderUnavailable("BMONI capability is unavailable until credentials and permissions are configured")
