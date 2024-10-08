# DnD Beyond Telegram Bot

## Usage

### Settings

#### Logging

- `LOGS__LEVEL` - logging level, can be one of `DEBUG`, `INFO`, `WARNING`, `ERROR`. Default is `INFO`.
- `LOGS__FORMAT` - logging format string, passed to python logging formatter. Default is `%(asctime)s - %(name)s - %(levelname)s - %(message)s`.

#### Telegram

- `TELEGRAM__TOKEN` - Telegram bot token.
- `TELEGRAM__BOT_NAME` - Telegram bot name.
- `TELEGRAM__BOT_SHORT_DESCRIPTION` - Telegram bot short description.
- `TELEGRAM__BOT_DESCRIPTION` - Telegram bot description.
- `TELEGRAM__HELP_MESSAGE_TEMPLATE` - Telegram bot help message template.
- `TELEGRAM__HELP_MESSAGE_ESCAPE_CHARACTERS` - Telegram bot help message escape characters. Default is `_-.`.

#### Context Repository

- `CONTEXT__TYPE` - context repository type, can be one of `local`, `redis`. Default is `local`.

##### Local

Context repository type `local` does not require any additional settings.

##### Redis

- `CONTEXT__HOST` - Redis host.
- `CONTEXT__PORT` - Redis port.
- `CONTEXT__DB` - Redis database.
- `CONTEXT__PASSWORD` - Redis password.

#### Character Service

- `CHARACTER__CACHE_TTL_SECONDS` - character cache time to live in seconds. Default is `3600`.

## Development

### Global dependencies

- poetry

### Taskfile commands

For all commands see [Taskfile](Taskfile.yaml) or `task --list-all`.
