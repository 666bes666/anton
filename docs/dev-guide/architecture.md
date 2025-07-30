# Architecture

The bot is designed with a modular and extensible architecture. Here are the key components:

-   **`main.py`**: The entry point of the application. It initializes the bot and runs it.
-   **`bot/core`**: Contains the core logic of the bot, including:
    -   `bot.py`: The main bot class, which handles events and loads cogs.
    -   `config.py`: Pydantic model for loading settings from environment variables.
    -   `scheduler.py`: The message scheduler, which handles sending messages at the configured time.
-   **`bot/cogs`**: Contains the command modules (cogs) for the bot. Each cog is a separate feature, such as configuration.
-   **`bot/utils`**: Contains utility functions and helper classes, such as the configuration manager.
-   **`data`**: Directory where the bot stores its data, including server configurations.
-   **`tests`**: Contains the test suite for the bot, including unit and integration tests.
