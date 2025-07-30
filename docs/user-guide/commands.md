# Commands

The bot supports the following slash commands:

## `/toggledaily <enable>`

Enable or disable daily messages for the server.

-   **`enable`**: Set to `true` to enable, `false` to disable.

## `/status`

Show the current configuration for the server, including:

-   **Status**: Whether daily messages are enabled or disabled.
-   **Channel**: The target channel for messages.
-   **Time**: The scheduled time in UTC.
-   **Message Preview**: A preview of the daily message.

All commands require the `Manage Server` permission.
