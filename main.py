
import asyncio
import logging
from bot.core.bot import DailyMessageBot
from bot.core.config import settings

# Configure logging
logging.basicConfig(level=logging.INFO, format="[%(asctime)s] [%(levelname)s] %(message)s")

async def main():
    """
    Initializes and runs the Discord bot.
    """
    if not settings.discord_bot_token:
        logging.error("DISCORD_BOT_TOKEN is not set in the .env file.")
        return

    bot = DailyMessageBot()

    try:
        await bot.start(settings.discord_bot_token)
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")
    finally:
        await bot.close()

if __name__ == "__main__":
    asyncio.run(main())
