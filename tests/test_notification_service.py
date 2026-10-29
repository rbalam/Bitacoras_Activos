import pytest
import asyncio
from unittest.mock import AsyncMock, patch, MagicMock
from backend.services.notification_service import NotificationService

@pytest.fixture
def mock_config_service():
    config_service = AsyncMock()
    # Default behavior
    config_service.get_resend_config.return_value = {
        "api_key": "test_api_key",
        "sender_email": "test@example.com"
    }
    return config_service

@pytest.fixture
def notification_service(mock_config_service):
    return NotificationService(config_service=mock_config_service)

@pytest.mark.asyncio
@patch('backend.services.notification_service.resend.Emails.send')
@patch('backend.services.notification_service.asyncio.to_thread')
async def test_send_email_success(mock_to_thread, mock_send, notification_service):
    # Setup
    mock_to_thread.return_value = {"id": "12345"}

    # Execute
    result = await notification_service.send_email(
        recipient_email="recipient@example.com",
        subject="Test Subject",
        html_content="<p>Test Content</p>"
    )

    # Assert
    assert result is True
    # mock_to_thread should be called once since that's how it's executed
    mock_to_thread.assert_called_once()

@pytest.mark.asyncio
async def test_send_email_missing_api_key(notification_service, mock_config_service):
    # Setup
    mock_config_service.get_resend_config.return_value = {
        "api_key": "",
        "sender_email": "test@example.com"
    }

    # Execute
    result = await notification_service.send_email(
        recipient_email="recipient@example.com",
        subject="Test Subject",
        html_content="<p>Test Content</p>"
    )

    # Assert
    assert result is False

@pytest.mark.asyncio
async def test_send_email_none_api_key(notification_service, mock_config_service):
    # Setup
    mock_config_service.get_resend_config.return_value = {
        "api_key": None,
        "sender_email": "test@example.com"
    }

    # Execute
    result = await notification_service.send_email(
        recipient_email="recipient@example.com",
        subject="Test Subject",
        html_content="<p>Test Content</p>"
    )

    # Assert
    assert result is False

@pytest.mark.asyncio
@patch('backend.services.notification_service.asyncio.to_thread')
async def test_send_email_exception(mock_to_thread, notification_service):
    # Setup
    mock_to_thread.side_effect = Exception("API Error")

    # Execute
    result = await notification_service.send_email(
        recipient_email="recipient@example.com",
        subject="Test Subject",
        html_content="<p>Test Content</p>"
    )

    # Assert
    assert result is False
    mock_to_thread.assert_called_once()
