import pytest
from unittest.mock import AsyncMock, patch

from services.notification_service import NotificationService

@pytest.fixture
def config_service():
    service = AsyncMock()
    service.get_resend_config.return_value = {
        "api_key": "test_api_key",
        "sender_email": "test@example.com"
    }
    return service

@pytest.fixture
def notification_service(config_service):
    return NotificationService(config_service)

@pytest.mark.asyncio
async def test_send_email_exception(notification_service, config_service):
    # Simulate an exception when calling resend.Emails.send
    with patch("services.notification_service.resend.Emails.send") as mock_send:
        mock_send.side_effect = Exception("Test exception")

        result = await notification_service.send_email(
            recipient_email="recipient@example.com",
            subject="Test Subject",
            html_content="<p>Test</p>"
        )

        assert result is False
