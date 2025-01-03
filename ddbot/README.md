# DnD Beyond Telegram Bot

## Usage

### Settings

#### Application

- `APP__ENV` - Application environment, can be one of `development`, `testing`, `staging`, `production`. Default is `production`.
- `APP__DEBUG` - Application debug mode, can be `true` or `false`. Default is `false`.

#### Logging

- `LOGS__LEVEL` - logging level, can be one of `DEBUG`, `INFO`, `WARNING`, `ERROR`. Default is `INFO`.
- `LOGS__FORMAT` - logging format string, passed to python logging formatter. Default is `%(asctime)s - %(name)s - %(levelname)s - %(message)s`.

#### Server

- `SERVER__HOST` - server host. Default is `localhost`.
- `SERVER__PORT` - server port. Default is `8080`.
- `SERVER__PUBLIC_HOST` - server public host.

#### Telegram

- `TELEGRAM__TOKEN` - Telegram bot token.
- `TELEGRAM__BOT_NAME` - Telegram bot name.
- `TELEGRAM__BOT_SHORT_DESCRIPTION` - Telegram bot short description.
- `TELEGRAM__BOT_DESCRIPTION` - Telegram bot description.
- `TELEGRAM__HELP_MESSAGE_TEMPLATE` - Telegram bot help message template.
- `TELEGRAM__HELP_MESSAGE_ESCAPE_CHARACTERS` - Telegram bot help message escape characters. Default is `_-.`.
- `TELEGRAM__WEBHOOK_ENABLED` - Telegram bot webhook enabled, can be `true` or `false`. Default is `True`.
- `TELEGRAM__WEBHOOK_URL` - Telegram bot webhook URL. Default is `/api/v1/telegram/webhook`.
- `TELEGRAM__WEBHOOK_SECRET_TOKEN` - Telegram bot webhook secret token.

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

- [poetry](https://python-poetry.org/docs/#installation)

### Taskfile commands

For all commands see [Taskfile](Taskfile.yaml) or `task --list-all`.
