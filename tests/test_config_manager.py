"""Tests for configuration manager."""
import asyncio
import json
import pytest
import tempfile
from pathlib import Path
from unittest.mock import AsyncMock, patch

from bot.utils.config_manager import ConfigManager

@pytest.fixture
async def temp_config_file():
    """Create a temporary config file for testing."""
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
        temp_path = Path(f.name)
    
    yield temp_path
    
    # Cleanup
    if temp_path.exists():
        temp_path.unlink()

@pytest.fixture
async def config_manager(temp_config_file):
    """Create a ConfigManager instance with a temporary file."""
    manager = ConfigManager(str(temp_config_file))
    await asyncio.sleep(0.1)  # Allow initial load to complete
    yield manager
    await manager.close()

class TestConfigManager:
    """Test ConfigManager functionality."""

    @pytest.mark.asyncio
    async def test_create_default_config(self, config_manager):
        """Test creating a default configuration."""
        guild_id = 12345
        await config_manager.create_default_config(guild_id)
        
        config = await config_manager.get_config(guild_id)
        
        assert config['channel_id'] is None
        assert config['time'] == '07:00'
        assert config['message'] == 'This is a default message. Please configure me!'
        assert config['enabled'] is False

    @pytest.mark.asyncio
    async def test_set_and_get_config(self, config_manager):
        """Test setting and getting configuration."""
        guild_id = 12345
        test_config = {
            'channel_id': 67890,
            'time': '10:30',
            'message': 'Test message',
            'enabled': True
        }
        
        await config_manager.set_config(guild_id, test_config)
        retrieved_config = await config_manager.get_config(guild_id)
        
        assert retrieved_config == test_config

    @pytest.mark.asyncio
    async def test_update_config(self, config_manager):
        """Test updating specific fields in configuration."""
        guild_id = 12345
        await config_manager.create_default_config(guild_id)
        
        updates = {'enabled': True, 'channel_id': 98765}
        await config_manager.update_config(guild_id, updates)
        
        config = await config_manager.get_config(guild_id)
        assert config['enabled'] is True
        assert config['channel_id'] == 98765
        assert config['time'] == '07:00'  # Should remain unchanged

    @pytest.mark.asyncio
    async def test_get_all_configs(self, config_manager):
        """Test retrieving all configurations."""
        # Create configs for multiple guilds
        guild_configs = {
            11111: {'channel_id': 1, 'enabled': True},
            22222: {'channel_id': 2, 'enabled': False},
        }
        
        for guild_id, config in guild_configs.items():
            await config_manager.set_config(guild_id, config)
        
        all_configs = await config_manager.get_all_configs()
        
        for guild_id, expected_config in guild_configs.items():
            assert guild_id in all_configs
            for key, value in expected_config.items():
                assert all_configs[guild_id][key] == value

    @pytest.mark.asyncio
    async def test_delete_config(self, config_manager):
        """Test deleting a configuration."""
        guild_id = 12345
        await config_manager.create_default_config(guild_id)
        
        # Verify config exists
        config = await config_manager.get_config(guild_id)
        assert config is not None and len(config) > 0
        
        # Delete config
        await config_manager.delete_config(guild_id)
        
        # Verify config is gone
        config = await config_manager.get_config(guild_id)
        assert config == {}

    @pytest.mark.asyncio
    async def test_get_nonexistent_config(self, config_manager):
        """Test getting configuration for non-existent guild."""
        config = await config_manager.get_config(99999)
        assert config == {}

    @pytest.mark.asyncio
    async def test_file_persistence(self, temp_config_file):
        """Test that configurations persist across manager instances."""
        guild_id = 12345
        test_config = {
            'channel_id': 67890,
            'time': '15:45',
            'message': 'Persistent test message',
            'enabled': True
        }
        
        # Create first manager and save config
        manager1 = ConfigManager(str(temp_config_file))
        await asyncio.sleep(0.1)  # Allow initial load
        await manager1.set_config(guild_id, test_config)
        await manager1.close()
        
        # Create second manager and verify config is loaded
        manager2 = ConfigManager(str(temp_config_file))
        await asyncio.sleep(0.1)  # Allow initial load
        retrieved_config = await manager2.get_config(guild_id)
        await manager2.close()
        
        assert retrieved_config == test_config

    @pytest.mark.asyncio
    async def test_load_corrupted_file(self, temp_config_file):
        """Test handling of corrupted configuration file."""
        # Write invalid JSON to the file
        with open(temp_config_file, 'w') as f:
            f.write("invalid json content")
        
        # Manager should handle the corruption gracefully
        manager = ConfigManager(str(temp_config_file))
        await asyncio.sleep(0.1)  # Allow initial load
        
        # Should start with empty configs
        all_configs = await manager.get_all_configs()
        assert all_configs == {}
        
        await manager.close()
