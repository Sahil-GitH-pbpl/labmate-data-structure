import logging
from typing import List

import httpx

from app.core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


def send_whatsapp_message(numbers: List[str], message: str) -> None:
    if not numbers:
        logger.info("No recipients provided for WhatsApp notification")
        return
    payload = {"to": numbers, "message": message}
    headers = {"Authorization": f"Bearer {settings.whatsapp_api_token}"}
    try:
        response = httpx.post(settings.whatsapp_api_url, json=payload, headers=headers, timeout=10)
        response.raise_for_status()
        logger.info("WhatsApp message sent: %s", payload)
    except Exception as exc:  # pragma: no cover - external integration
        logger.error("Failed to send WhatsApp message: %s", exc)
