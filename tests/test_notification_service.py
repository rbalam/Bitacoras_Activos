import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from services.notification_service import NotificationService

@pytest.fixture
def mock_config_service():
    service = AsyncMock()
    return service

@pytest.fixture
def notification_service(mock_config_service):
    return NotificationService(config_service=mock_config_service)

@pytest.mark.asyncio
async def test_send_whatsapp_missing_config(notification_service, mock_config_service):
    """Test that it returns False if Twilio client or whatsapp_from is missing"""
    # Configure mock to return empty config
    mock_config_service.get_twilio_config.return_value = {}

    result = await notification_service.send_whatsapp("1234567890", "Test message")

    assert result is False

@pytest.mark.asyncio
async def test_send_whatsapp_success(notification_service, mock_config_service):
    """Test successful WhatsApp message send"""
    # Mock config
    mock_config_service.get_twilio_config.return_value = {
        "account_sid": "test_sid",
        "auth_token": "test_token",
        "whatsapp_from": "whatsapp:+1234567890"
    }

    # Mock Twilio Client
    mock_twilio_client = MagicMock()
    mock_messages = MagicMock()
    mock_message_obj = MagicMock()
    mock_message_obj.sid = "test_message_sid"

    # asyncio.to_thread needs a function that returns the result
    def mock_create(*args, **kwargs):
        return mock_message_obj
    mock_messages.create = mock_create
    mock_twilio_client.messages = mock_messages

    # Patch the _get_twilio_client to return our mock
    with patch.object(notification_service, '_get_twilio_client', return_value=mock_twilio_client):
        result = await notification_service.send_whatsapp("whatsapp:+0987654321", "Test message")

        assert result is True

@pytest.mark.asyncio
async def test_send_whatsapp_format_number(notification_service, mock_config_service):
    """Test that numbers without 'whatsapp:' prefix are formatted correctly"""
    mock_config_service.get_twilio_config.return_value = {
        "account_sid": "test_sid",
        "auth_token": "test_token",
        "whatsapp_from": "+1234567890" # Missing prefix
    }

    mock_twilio_client = MagicMock()
    mock_messages = MagicMock()
    mock_message_obj = MagicMock()

    create_called_with = {}

    def mock_create(*args, **kwargs):
        create_called_with.update(kwargs)
        return mock_message_obj

    mock_messages.create = mock_create
    mock_twilio_client.messages = mock_messages

    with patch.object(notification_service, '_get_twilio_client', return_value=mock_twilio_client):
        result = await notification_service.send_whatsapp("0987654321", "Test message") # Missing prefix

        assert result is True
        assert create_called_with.get('to') == "whatsapp:0987654321"
        assert create_called_with.get('from_') == "whatsapp:+1234567890"

@pytest.mark.asyncio
async def test_send_whatsapp_exception(notification_service, mock_config_service):
    """Test that it returns False if an exception occurs during sending"""
    mock_config_service.get_twilio_config.return_value = {
        "account_sid": "test_sid",
        "auth_token": "test_token",
        "whatsapp_from": "whatsapp:+1234567890"
    }

    mock_twilio_client = MagicMock()
    mock_messages = MagicMock()

    def mock_create(*args, **kwargs):
        raise Exception("API Error")

    mock_messages.create = mock_create
    mock_twilio_client.messages = mock_messages

    with patch.object(notification_service, '_get_twilio_client', return_value=mock_twilio_client):
        result = await notification_service.send_whatsapp("whatsapp:+0987654321", "Test message")

        assert result is False
