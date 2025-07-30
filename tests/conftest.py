"""Fixtures and configurations for pytest."""

import pytest
from unittest.mock import MagicMock

@pytest.fixture
def mock_bot():
    """Fixture to create a mock bot instance."""
    # Create a mock bot with necessary attributes and methods
    bot = MagicMock()
    bot.user.name = "TestBot"
    bot.user.id = 123456789
    
    # Mock config manager
    bot.config_manager = MagicMock()
    bot.config_manager.get_config.return_value = { # Mock async method
        'channel_id': 98765,
        'time': '08:00',
        'message': 'Test message',
        'enabled': True
    }

    # Mock scheduler
    bot.scheduler = MagicMock()
    
    return bot
