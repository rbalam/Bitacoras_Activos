import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from services.notification_service import NotificationService

@pytest.fixture
def mock_config_service():
    return AsyncMock()

@pytest.fixture
def notification_service(mock_config_service):
    return NotificationService(mock_config_service)

@pytest.mark.asyncio
async def test_send_whatsapp_success(notification_service, mock_config_service):
    # Setup mocks
    mock_twilio_client = MagicMock()
    mock_message = MagicMock()
    mock_message.sid = "test_sid_123"
    mock_twilio_client.messages.create.return_value = mock_message

    mock_config_service.get_twilio_config.return_value = {
        "whatsapp_from": "whatsapp:+1234567890"
    }

    # Mock _get_twilio_client to return our mock
    with patch.object(notification_service, '_get_twilio_client', new_callable=AsyncMock) as mock_get_client:
        mock_get_client.return_value = mock_twilio_client

        # Call method
        result = await notification_service.send_whatsapp("whatsapp:+0987654321", "Test message")

        # Assertions
        assert result is True
        mock_get_client.assert_called_once()
        mock_config_service.get_twilio_config.assert_called_once()
        mock_twilio_client.messages.create.assert_called_once_with(
            body="Test message",
            from_="whatsapp:+1234567890",
            to="whatsapp:+0987654321"
        )

@pytest.mark.asyncio
async def test_send_whatsapp_unformatted_numbers(notification_service, mock_config_service):
    # Setup mocks
    mock_twilio_client = MagicMock()
    mock_message = MagicMock()
    mock_message.sid = "test_sid_123"
    mock_twilio_client.messages.create.return_value = mock_message

    mock_config_service.get_twilio_config.return_value = {
        "whatsapp_from": "+1234567890"  # Missing 'whatsapp:' prefix
    }

    # Mock _get_twilio_client
    with patch.object(notification_service, '_get_twilio_client', new_callable=AsyncMock) as mock_get_client:
        mock_get_client.return_value = mock_twilio_client

        # Call method with unformatted phone number
        result = await notification_service.send_whatsapp("+0987654321", "Test message")

        # Assertions
        assert result is True
        mock_twilio_client.messages.create.assert_called_once_with(
            body="Test message",
            from_="whatsapp:+1234567890", # Should have prefix added
            to="whatsapp:+0987654321"   # Should have prefix added
        )

@pytest.mark.asyncio
async def test_send_whatsapp_missing_config(notification_service, mock_config_service):
    # Test missing whatsapp_from
    mock_config_service.get_twilio_config.return_value = {}

    with patch.object(notification_service, '_get_twilio_client', new_callable=AsyncMock) as mock_get_client:
        mock_get_client.return_value = MagicMock()

        result = await notification_service.send_whatsapp("whatsapp:+0987654321", "Test message")
        assert result is False

    # Test missing twilio_client
    mock_config_service.get_twilio_config.return_value = {
        "whatsapp_from": "whatsapp:+1234567890"
    }

    with patch.object(notification_service, '_get_twilio_client', new_callable=AsyncMock) as mock_get_client:
        mock_get_client.return_value = None

        result = await notification_service.send_whatsapp("whatsapp:+0987654321", "Test message")
        assert result is False

@pytest.mark.asyncio
async def test_send_whatsapp_api_exception(notification_service, mock_config_service):
    # Setup mocks
    mock_twilio_client = MagicMock()
    mock_twilio_client.messages.create.side_effect = Exception("Twilio API Error")

    mock_config_service.get_twilio_config.return_value = {
        "whatsapp_from": "whatsapp:+1234567890"
    }

    # Mock _get_twilio_client
    with patch.object(notification_service, '_get_twilio_client', new_callable=AsyncMock) as mock_get_client:
        mock_get_client.return_value = mock_twilio_client

        # Call method
        result = await notification_service.send_whatsapp("whatsapp:+0987654321", "Test message")

        # Assertions
        assert result is False
