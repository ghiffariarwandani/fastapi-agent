from agents.extensions.models.litellm_model import LitellmModel

from app.core.settings import settings

llm_model = LitellmModel(
    base_url=settings.OPENROUTER_BASE_URL,
    api_key=settings.OPENROUTER_API_KEY,
    model="openai/gpt-oss-120b",
)
