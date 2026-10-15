import pytest
from unittest.mock import AsyncMock, patch, MagicMock
import asyncio
import resend

from backend.services.notification_service import NotificationService

@pytest.fixture
def mock_config_service():
    config_service = MagicMock()
    config_service.get_resend_config = AsyncMock()
    config_service.get_twilio_config = AsyncMock()
    return config_service

@pytest.fixture
def notification_service(mock_config_service):
    return NotificationService(mock_config_service)

@pytest.mark.asyncio
async def test_send_email_success(notification_service, mock_config_service):
    mock_config_service.get_resend_config.return_value = {
        "api_key": "test_api_key",
        "sender_email": "test@sender.com"
    }

    with patch("backend.services.notification_service.asyncio.to_thread", new_callable=AsyncMock) as mock_to_thread:
        mock_to_thread.return_value = {"id": "email_id_123"}

        result = await notification_service.send_email("test@recipient.com", "Subject", "<p>HTML</p>")

        assert result is True
        mock_to_thread.assert_called_once()
        args, kwargs = mock_to_thread.call_args
        # args[0] should be resend.Emails.send
        assert args[0] == resend.Emails.send
        params = args[1]
        assert params["from"] == "test@sender.com"
        assert params["to"] == ["test@recipient.com"]
        assert params["subject"] == "Subject"
        assert params["html"] == "<p>HTML</p>"

@pytest.mark.asyncio
async def test_send_email_no_api_key(notification_service, mock_config_service):
    mock_config_service.get_resend_config.return_value = {
        "api_key": "",
        "sender_email": "test@sender.com"
    }

    result = await notification_service.send_email("test@recipient.com", "Subject", "<p>HTML</p>")

    assert result is False

@pytest.mark.asyncio
async def test_send_email_exception(notification_service, mock_config_service):
    mock_config_service.get_resend_config.return_value = {
        "api_key": "test_api_key",
        "sender_email": "test@sender.com"
    }

    with patch("backend.services.notification_service.asyncio.to_thread", new_callable=AsyncMock) as mock_to_thread:
        mock_to_thread.side_effect = Exception("API error")

        result = await notification_service.send_email("test@recipient.com", "Subject", "<p>HTML</p>")

        assert result is False

@pytest.mark.asyncio
async def test_send_email_no_sender_email(notification_service, mock_config_service):
    mock_config_service.get_resend_config.return_value = {
        "api_key": "test_api_key",
        "sender_email": None
    }

    with patch("backend.services.notification_service.asyncio.to_thread", new_callable=AsyncMock) as mock_to_thread:
        mock_to_thread.return_value = {"id": "email_id_123"}

        result = await notification_service.send_email("test@recipient.com", "Subject", "<p>HTML</p>")

        assert result is True
        args, _ = mock_to_thread.call_args
        params = args[1]
        assert params["from"] == "onboarding@resend.dev"
