# Discord Daily Message Bot

A professional, production-ready Discord bot for sending scheduled daily messages, built with a focus on clean architecture, maintainability, and modern DevOps practices.

[![CI](https://github.com/666bes666/anton/actions/workflows/ci.yml/badge.svg)](https://github.com/666bes666/anton/actions/workflows/ci.yml)
[![CD](https://github.com/666bes666/anton/actions/workflows/cd.yml/badge.svg)](https://github.com/666bes666/anton/actions/workflows/cd.yml)
[![Codecov](https://codecov.io/gh/666bes666/anton/branch/main/graph/badge.svg)](https://codecov.io/gh/666bes666/anton)

## Features

- **Easy Configuration**: Set up the bot through a user-friendly modal interface in Discord.
- **Per-Server Settings**: Customize messages, channels, and schedules for each server.
- **Robust and Reliable**: Built with modern Python, including async operations, type hints, and extensive error handling.
- **Extensible**: The bot's architecture is designed for easy extension with new features and commands.
- **DevOps-Ready**: Includes a full CI/CD pipeline, Docker support, and detailed documentation.

## Documentation

For detailed information on installation, configuration, and development, please see the [**full documentation**](https://666bes666.github.io/anton/).

## Getting Started

To get the bot up and running, follow these steps:

1.  **Clone the repository**:
    ```bash
    git clone https://github.com/666bes666/anton.git
    cd anton
    ```

2.  **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

3.  **Set up environment variables**: Copy `.env.example` to `.env` and add your Discord bot token.

4.  **Run the bot**:
    ```bash
    python main.py
    ```

## Contributing

Contributions are welcome! Please see the [**contributing guide**](docs/dev-guide/contributing.md) for more information.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
