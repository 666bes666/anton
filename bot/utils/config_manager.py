"""Configuration manager for guild settings."""
import asyncio
import json
import logging
import os
from pathlib import Path
from typing import Dict, Any, Optional

import aiofiles

logger = logging.getLogger(__name__)

class ConfigManager:
    """
    Manages guild configurations with async file operations and proper error handling.
    """
    
    def __init__(self, config_file_path: str):
        self.config_file_path = Path(config_file_path)
        self._configs: Dict[int, Dict[str, Any]] = {}
        self._lock = asyncio.Lock()
        
        # Ensure the directory exists
        self.config_file_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Load existing configurations
        asyncio.create_task(self._load_configs())
        
    async def _load_configs(self):
        """Load configurations from file."""
        async with self._lock:
            try:
                if self.config_file_path.exists():
                    async with aiofiles.open(self.config_file_path, 'r') as f:
                        content = await f.read()
                        loaded_configs = json.loads(content)
                        # Convert string guild IDs back to integers
                        self._configs = {int(k): v for k, v in loaded_configs.items()}
                        logger.info(f"Loaded {len(self._configs)} guild configurations")
                else:
                    logger.info("No existing configuration file found, starting with empty configs")
                    self._configs = {}
            except Exception as e:
                logger.error(f"Failed to load configurations: {e}")
                self._configs = {}
                
    async def _save_configs(self):
        """Save configurations to file."""
        async with self._lock:
            try:
                # Convert integer guild IDs to strings for JSON serialization
                configs_to_save = {str(k): v for k, v in self._configs.items()}
                
                async with aiofiles.open(self.config_file_path, 'w') as f:
                    await f.write(json.dumps(configs_to_save, indent=4))
                    
                logger.debug("Configurations saved successfully")
            except Exception as e:
                logger.error(f"Failed to save configurations: {e}")
                
    async def get_config(self, guild_id: int) -> Dict[str, Any]:
        """Get configuration for a specific guild."""
        return self._configs.get(guild_id, {})
        
    async def set_config(self, guild_id: int, config: Dict[str, Any]):
        """Set configuration for a specific guild."""
        self._configs[guild_id] = config
        await self._save_configs()
        
    async def update_config(self, guild_id: int, updates: Dict[str, Any]):
        """Update specific fields in a guild's configuration."""
        if guild_id not in self._configs:
            await self.create_default_config(guild_id)
            
        self._configs[guild_id].update(updates)
        await self._save_configs()
        
    async def get_all_configs(self) -> Dict[int, Dict[str, Any]]:
        """Get all guild configurations."""
        return self._configs.copy()
        
    async def create_default_config(self, guild_id: int):
        """Create a default configuration for a new guild."""
        default_config = {
            'channel_id': None,
            'time': '07:00',
            'message': 'This is a default message. Please configure me!',
            'enabled': False
        }
        
        if guild_id not in self._configs:
            self._configs[guild_id] = default_config
            await self._save_configs()
            logger.info(f"Created default configuration for guild {guild_id}")
            
    async def delete_config(self, guild_id: int):
        """Delete configuration for a guild."""
        if guild_id in self._configs:
            del self._configs[guild_id]
            await self._save_configs()
            logger.info(f"Deleted configuration for guild {guild_id}")
            
    async def close(self):
        """Clean up resources."""
        await self._save_configs()
