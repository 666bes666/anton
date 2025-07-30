import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime, time
import json
import os
import tempfile

# Import the bot components
from discord_bot import DailyMessageBot, SettingsModal


class TestDailyMessageBot:
    """Test cases for the DailyMessageBot class."""

    @pytest.fixture
    def temp_config_file(self):
        """Create a temporary config file for testing."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump({}, f)
            temp_file = f.name
        
        # Patch the CONFIG_FILE constant
        with patch('discord_bot.CONFIG_FILE', temp_file):
            yield temp_file
        
        # Clean up
        os.unlink(temp_file)

    @pytest.fixture
    def mock_bot_token(self):
        """Mock the bot token environment variable."""
        with patch.dict(os.environ, {'DISCORD_BOT_TOKEN': 'mock_token'}):
            yield

    def test_load_configs_empty_file(self, temp_config_file):
        """Test loading configurations from an empty file."""
        with patch('discord_bot.CONFIG_FILE', temp_config_file):
            bot = DailyMessageBot()
            assert bot.configs == {}

    def test_load_configs_with_data(self, temp_config_file):
        """Test loading configurations with existing data."""
        test_data = {
            "123456789": {
                "channel_id": 987654321,
                "time": "07:00",
                "message": "Test message",
                "enabled": True
            }
        }
        
        with open(temp_config_file, 'w') as f:
            json.dump(test_data, f)
        
        with patch('discord_bot.CONFIG_FILE', temp_config_file):
            bot = DailyMessageBot()
            expected = {123456789: test_data["123456789"]}
            assert bot.configs == expected

    def test_save_configs(self, temp_config_file):
        """Test saving configurations to file."""
        with patch('discord_bot.CONFIG_FILE', temp_config_file):
            bot = DailyMessageBot()
            bot.configs = {
                123456789: {
                    "channel_id": 987654321,
                    "time": "07:00",
                    "message": "Test message",
                    "enabled": True
                }
            }
            bot.save_configs()
            
            # Verify the file was written correctly
            with open(temp_config_file, 'r') as f:
                saved_data = json.load(f)
            
            expected = {
                "123456789": {
                    "channel_id": 987654321,
                    "time": "07:00",
                    "message": "Test message",
                    "enabled": True
                }
            }
            assert saved_data == expected

    def test_get_guild_config_existing(self, temp_config_file):
        """Test retrieving configuration for an existing guild."""
        with patch('discord_bot.CONFIG_FILE', temp_config_file):
            bot = DailyMessageBot()
            bot.configs = {
                123456789: {
                    "channel_id": 987654321,
                    "time": "07:00",
                    "message": "Test message",
                    "enabled": True
                }
            }
            
            config = bot.get_guild_config(123456789)
            expected = {
                "channel_id": 987654321,
                "time": "07:00",
                "message": "Test message",
                "enabled": True
            }
            assert config == expected

    def test_get_guild_config_nonexistent(self, temp_config_file):
        """Test retrieving configuration for a non-existent guild."""
        with patch('discord_bot.CONFIG_FILE', temp_config_file):
            bot = DailyMessageBot()
            config = bot.get_guild_config(999999999)
            assert config == {}

    @pytest.mark.asyncio
    async def test_on_guild_join(self, temp_config_file):
        """Test bot behavior when joining a new guild."""
        with patch('discord_bot.CONFIG_FILE', temp_config_file):
            bot = DailyMessageBot()
            
            # Mock guild object
            mock_guild = Mock()
            mock_guild.id = 123456789
            mock_guild.name = "Test Guild"
            
            await bot.on_guild_join(mock_guild)
            
            # Check that default config was created
            assert 123456789 in bot.configs
            config = bot.configs[123456789]
            assert config["channel_id"] is None
            assert config["time"] == "07:00"
            assert config["message"] == "This is a default message. Please configure me!"
            assert config["enabled"] is False


class TestSettingsModal:
    """Test cases for the SettingsModal class."""

    @pytest.fixture
    def mock_bot(self):
        """Create a mock bot for testing."""
        bot = Mock()
        bot.get_guild_config.return_value = {
            "channel_id": "123456789",
            "time": "07:00",
            "message": "Test message"
        }
        bot.save_configs = Mock()
        bot.configs = {}
        return bot

    @pytest.fixture
    def settings_modal(self, mock_bot):
        """Create a SettingsModal instance for testing."""
        return SettingsModal(mock_bot, 123456789)

    def test_modal_initialization(self, settings_modal, mock_bot):
        """Test that the modal initializes correctly with existing config."""
        assert settings_modal.bot == mock_bot
        assert settings_modal.guild_id == 123456789
        
        # Check that inputs are created
        assert hasattr(settings_modal, 'channel_id_input')
        assert hasattr(settings_modal, 'time_input')
        assert hasattr(settings_modal, 'message_input')

    @pytest.mark.asyncio
    async def test_on_submit_valid_input(self, settings_modal, mock_bot):
        """Test modal submission with valid input."""
        # Mock the interaction
        mock_interaction = AsyncMock()
        
        # Set up input values
        settings_modal.channel_id_input.value = "987654321"
        settings_modal.time_input.value = "09:30"
        settings_modal.message_input.value = "Good morning!"
        
        await settings_modal.on_submit(mock_interaction)
        
        # Check that config was saved
        expected_config = {
            'channel_id': 987654321,
            'time': '09:30',
            'message': 'Good morning!',
            'enabled': True
        }
        assert mock_bot.configs[123456789] == expected_config
        mock_bot.save_configs.assert_called_once()
        mock_interaction.response.send_message.assert_called_once()

    @pytest.mark.asyncio
    async def test_on_submit_invalid_channel_id(self, settings_modal, mock_bot):
        """Test modal submission with invalid channel ID."""
        mock_interaction = AsyncMock()
        
        # Set up invalid input
        settings_modal.channel_id_input.value = "not_a_number"
        settings_modal.time_input.value = "09:30"
        settings_modal.message_input.value = "Good morning!"
        
        await settings_modal.on_submit(mock_interaction)
        
        # Check that error message was sent
        mock_interaction.response.send_message.assert_called_once()
        args = mock_interaction.response.send_message.call_args[0]
        assert "Invalid Channel ID" in args[0]
        assert mock_bot.save_configs.call_count == 0

    @pytest.mark.asyncio
    async def test_on_submit_invalid_time_format(self, settings_modal, mock_bot):
        """Test modal submission with invalid time format."""
        mock_interaction = AsyncMock()
        
        # Set up invalid input
        settings_modal.channel_id_input.value = "987654321"
        settings_modal.time_input.value = "25:00"  # Invalid hour
        settings_modal.message_input.value = "Good morning!"
        
        await settings_modal.on_submit(mock_interaction)
        
        # Check that error message was sent
        mock_interaction.response.send_message.assert_called_once()
        args = mock_interaction.response.send_message.call_args[0]
        assert "Invalid time format" in args[0]
        assert mock_bot.save_configs.call_count == 0


class TestUtilityFunctions:
    """Test utility functions and edge cases."""

    def test_time_parsing(self):
        """Test time parsing functionality."""
        # Valid time formats
        valid_times = ["07:00", "23:59", "00:00", "12:30"]
        for time_str in valid_times:
            parsed_time = datetime.strptime(time_str, '%H:%M').time()
            assert isinstance(parsed_time, time)

        # Invalid time formats should raise ValueError
        invalid_times = ["25:00", "12:60", "7:00", "12:3", "invalid"]
        for time_str in invalid_times:
            with pytest.raises(ValueError):
                datetime.strptime(time_str, '%H:%M').time()

    def test_channel_id_validation(self):
        """Test channel ID validation."""
        # Valid channel IDs (numeric strings)
        valid_ids = ["123456789", "987654321", "1"]
        for channel_id in valid_ids:
            assert int(channel_id) > 0

        # Invalid channel IDs
        invalid_ids = ["not_a_number", "", "12.34", "-123"]
        for channel_id in invalid_ids:
            with pytest.raises(ValueError):
                int(channel_id)


# Integration test placeholder
class TestBotIntegration:
    """Integration tests for bot functionality."""

    @pytest.mark.asyncio
    async def test_daily_message_sender_disabled_config(self):
        """Test that daily message sender skips disabled configurations."""
        # This would require more complex mocking of discord.py objects
        # For now, this serves as a placeholder for integration tests
        pass

    @pytest.mark.asyncio  
    async def test_daily_message_sender_invalid_channel(self):
        """Test that daily message sender handles invalid channels gracefully."""
        # Placeholder for integration test
        pass


if __name__ == "__main__":
    pytest.main([__file__])
