# Discord Daily Message Bot

A Python Discord bot that sends daily messages to a specified channel at a scheduled time, configurable through Discord's user interface.

## Features

- **Context Menu Configuration**: Configure the bot by right-clicking on it in Discord
- **Per-Server Settings**: Each server can have its own schedule and message
- **Modal Dialog Interface**: Easy-to-use settings form within Discord
- **Enable/Disable Toggle**: Use `/toggledaily` command to enable/disable messages
- **Persistent Storage**: Settings are saved to a JSON file and persist across restarts
- **Production-ready**: Proper error handling, validation, and logging
- **Timezone-aware**: Uses UTC time for consistent scheduling

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Create Discord Bot

1. Go to the [Discord Developer Portal](https://discord.com/developers/applications)
2. Click "New Application" and give it a name
3. Go to the "Bot" section
4. Click "Add Bot"
5. Copy the bot token (you'll need this for the `.env` file)
6. Under "Privileged Gateway Intents", you may need to enable "Message Content Intent" if your bot needs to read messages

### 3. Invite Bot to Your Server

1. In the Developer Portal, go to "OAuth2" → "URL Generator"
2. Select "bot" in Scopes
3. Select "Send Messages" in Bot Permissions
4. Copy the generated URL and open it in your browser
5. Select your server and authorize the bot

### 4. Set Up Bot Token

1. Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` and add your bot token:
   - `DISCORD_BOT_TOKEN`: Your bot token from the Developer Portal

### 5. Configure Through Discord UI

Once the bot is running and in your server, you can configure it entirely through Discord:

1. **Right-click on the bot** in the member list or any message from the bot
2. **Select "Apps" → "Configure Bot"** from the context menu
3. **Fill out the configuration modal**:
   - **Target Channel ID**: The numeric ID of the channel for daily messages
   - **Send Time**: Time in UTC (24-hour format, e.g., "07:00" for 10:00 MSK)
   - **Daily Message Content**: The message to send daily
4. **Click "Submit"** to save your settings

**To get a channel ID:**
- Enable Developer Mode in Discord (User Settings → Advanced → Developer Mode)
- Right-click on the target channel and select "Copy Channel ID"

**Additional Commands:**
- Use `/toggledaily true` to enable daily messages
- Use `/toggledaily false` to disable daily messages

## Running the Bot

```bash
python discord_bot.py
```

The bot will:
1. Log in to Discord
2. Calculate the next scheduled message time
3. Wait until that time and send the message
4. Repeat daily

## Customization Examples

### Adding New Message Scenarios

```python
MESSAGES = {
    "inspiration": "Good morning, team! Here's your daily inspiration: Stay focused and keep building!",
    "reminder": "Friendly reminder: The team meeting is today at 2 PM. Be there!",
    "fun_fact": "Did you know? A group of flamingos is called a flamboyance. Have a great day!",
    "weekly_goals": "It's Monday! Time to set your weekly goals and crush them! 💪"
}
```

### Changing the Schedule

```python
# For 9:00 AM EST (14:00 UTC)
SCHEDULED_TIME_UTC = time(14, 0)

# For 6:00 PM PST (02:00 UTC next day)
SCHEDULED_TIME_UTC = time(2, 0)
```

### Dynamic Message Content

You can modify the bot to use dynamic content:

```python
import random

def get_dynamic_message():
    quotes = [
        "The only way to do great work is to love what you do. - Steve Jobs",
        "Innovation distinguishes between a leader and a follower. - Steve Jobs",
        "Life is what happens to you while you're busy making other plans. - John Lennon"
    ]
    return f"Daily inspiration: {random.choice(quotes)}"
```

## Production Deployment

For production deployment, consider:

1. **Process Management**: Use a process manager like `systemd`, `supervisor`, or `pm2`
2. **Logging**: Add proper logging instead of print statements
3. **Monitoring**: Monitor the bot's health and uptime
4. **Error Recovery**: The bot includes automatic reconnection, but monitor for issues
5. **Resource Management**: The bot is lightweight but monitor memory usage over time

## Troubleshooting

### Bot doesn't send messages
- Check that the bot has "Send Messages" permission in the target channel
- Verify the channel ID is correct
- Ensure the bot is in the server

### Authentication errors
- Double-check your bot token in the `.env` file
- Make sure there are no extra spaces or quotes around the token

### Time zone issues
- The bot uses UTC time internally
- Convert your desired local time to UTC when setting `SCHEDULED_TIME_UTC`

## License

This project is open source and available under the MIT License.
# Test commit to verify secrets
