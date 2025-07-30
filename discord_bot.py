# main.py

import discord
from discord.ext import commands
from discord import app_commands, ui, Interaction
import asyncio
import json
from datetime import datetime, time
import os
from dotenv import load_dotenv

# --- SETUP ---
# Load environment variables
load_dotenv()
BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")

# Configuration file to store settings for each server
CONFIG_FILE = 'server_configs.json'

# --- BOT IMPLEMENTATION ---

# Define the modal for settings
class SettingsModal(ui.Modal, title='Configure Daily Messages'):
    def __init__(self, bot, guild_id):
        super().__init__()
        self.bot = bot
        self.guild_id = guild_id
        
        # Get current settings to pre-fill the form
        current_config = self.bot.get_guild_config(self.guild_id)
        
        # UI components for the modal
        self.channel_id_input = ui.TextInput(
            label='Target Channel ID',
            placeholder='Enter the ID of the channel for daily messages',
            default=current_config.get('channel_id')
        )
        self.time_input = ui.TextInput(
            label='Send Time (UTC, 24-hour format)',
            placeholder='e.g., 07:00 for 10:00 MSK',
            default=current_config.get('time')
        )
        self.message_input = ui.TextInput(
            label='Daily Message Content',
            style=discord.TextStyle.paragraph,
            placeholder='Type the message you want to send daily.',
            default=current_config.get('message')
        )
        
        self.add_item(self.channel_id_input)
        self.add_item(self.time_input)
        self.add_item(self.message_input)

    async def on_submit(self, interaction: Interaction):
        # Retrieve user inputs
        channel_id_str = self.channel_id_input.value
        time_str = self.time_input.value
        message = self.message_input.value

        # Validate inputs
        try:
            channel_id = int(channel_id_str)
        except ValueError:
            await interaction.response.send_message("Invalid Channel ID. Please provide a numeric ID.", ephemeral=True)
            return

        try:
            # Validate time format HH:MM
            scheduled_time = datetime.strptime(time_str, '%H:%M').time()
        except ValueError:
            await interaction.response.send_message("Invalid time format. Please use HH:MM (e.g., 07:00).", ephemeral=True)
            return
        
        # Save the new configuration
        self.bot.configs[self.guild_id] = {
            'channel_id': channel_id,
            'time': time_str,
            'message': message,
            'enabled': True
        }
        self.bot.save_configs()

        await interaction.response.send_message(
            f"✅ **Settings updated!**\n"
            f"Daily messages will be sent to channel `{channel_id}` at `{time_str}` UTC.\n"
            f"To disable, use the `/toggledaily a` command.",
            ephemeral=True
        )

# Main bot class
class DailyMessageBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        super().__init__(command_prefix='!', intents=intents)
        self.configs = self.load_configs()
        self.last_sent_time = {} # Tracks when a message was last sent to a guild
        self.bg_task = self.loop.create_task(self.daily_message_sender())
        self.add_app_commands()
        
    def load_configs(self):
        try:
            with open(CONFIG_FILE, 'r') as f:
                # Convert string guild IDs back to int
                return {int(k): v for k, v in json.load(f).items()}
        except (FileNotFoundError, json.JSONDecodeError):
            return {}

    def save_configs(self):
        with open(CONFIG_FILE, 'w') as f:
            json.dump(self.configs, f, indent=4)

    def get_guild_config(self, guild_id):
        return self.configs.get(guild_id, {})
        
    def add_app_commands(self):
        # Context Menu Command (right-click on the bot)
        @self.tree.context_menu(name="Configure Bot")
        @app_commands.checks.has_permissions(manage_guild=True)
        async def configure_bot_context_menu(interaction: Interaction, user: discord.Member):
            modal = SettingsModal(self, interaction.guild_id)
            await interaction.response.send_modal(modal)

        # Slash command to enable/disable
        @self.tree.command(name="toggledaily", description="Enable or disable daily messages for this server.")
        @app_commands.checks.has_permissions(manage_guild=True)
        async def toggle_command(interaction: Interaction, enable: bool):
            if interaction.guild_id in self.configs:
                self.configs[interaction.guild_id]['enabled'] = enable
                self.save_configs()
                status = "enabled" if enable else "disabled"
                await interaction.response.send_message(f"Daily messages have been **{status}**.", ephemeral=True)
            else:
                await interaction.response.send_message("Please configure the bot first using the 'Configure Bot' context menu.", ephemeral=True)

    async def on_ready(self):
        print(f'Logged in as {self.user.name}')
        print(f'Syncing application commands...')
        await self.tree.sync()
        print('Commands synced. Bot is ready.')

    async def on_guild_join(self, guild):
        # Create a default, disabled config when the bot joins a new server
        if guild.id not in self.configs:
            self.configs[guild.id] = {
                'channel_id': None,
                'time': "07:00",
                'message': "This is a default message. Please configure me!",
                'enabled': False
            }
            self.save_configs()
            print(f"Joined new guild {guild.name}. Created default config.")

    async def daily_message_sender(self):
        await self.wait_until_ready()
        
        while not self.is_closed():
            now_utc = datetime.utcnow()
            
            # Iterate over a copy, as configs can be modified
            for guild_id, config in list(self.configs.items()):
                if not config.get('enabled') or not config.get('channel_id'):
                    continue

                # Check if we have already sent a message today
                last_sent_date = self.last_sent_time.get(guild_id)
                if last_sent_date == now_utc.date():
                    continue

                # Check if it's time to send
                try:
                    scheduled_time = datetime.strptime(config['time'], '%H:%M').time()
                    if scheduled_time.hour == now_utc.hour and scheduled_time.minute == now_utc.minute:
                        channel = self.get_channel(config['channel_id'])
                        if channel:
                            try:
                                await channel.send(config['message'])
                                self.last_sent_time[guild_id] = now_utc.date()
                                print(f"Sent daily message to guild {guild_id}")
                            except discord.Forbidden:
                                print(f"Error: No permission to send in channel {config['channel_id']} for guild {guild_id}")
                        else:
                            print(f"Error: Channel {config['channel_id']} not found for guild {guild_id}")
                except (ValueError, KeyError):
                    # Handle invalid time format or missing keys
                    continue
            
            # Wait for 60 seconds before checking again
            await asyncio.sleep(60)

def main():
    if not BOT_TOKEN:
        print("Error: DISCORD_BOT_TOKEN is not set in the .env file.")
        return
        
    bot = DailyMessageBot()
    
    try:
        bot.run(BOT_TOKEN)
    except discord.LoginFailure:
        print("Error: Login failed. Check if your bot token is correct.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    main()

