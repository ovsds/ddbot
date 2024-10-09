# DnD Beyond Telegram Bot

## Usage

### Settings

#### Logging

`LOGS__LEVEL` - logging level, can be one of `DEBUG`, `INFO`, `WARNING`, `ERROR`. Default is `INFO`.
`LOGS__FORMAT` - logging format string, passed to python logging formatter. Default is `%(asctime)s - %(name)s - %(levelname)s - %(message)s`.

#### Telegram

`TELEGRAM__TOKEN` - Telegram bot token.
`TELEGRAM__BOT_NAME` - Telegram bot name.
`TELEGRAM__BOT_SHORT_DESCRIPTION` - Telegram bot short description.
`TELEGRAM__BOT_DESCRIPTION` - Telegram bot description.

#### Context Repository

`CONTEXT__TYPE` - context repository type, can be one of `local`, `redis`. Default is `local`.

##### Local

Context repository type `local` does not require any additional settings.

##### Redis

`CONTEXT__REDIS_HOST` - Redis host.
`CONTEXT__REDIS_PORT` - Redis port.
`CONTEXT__REDIS_DB` - Redis database.
`CONTEXT__REDIS_PASSWORD` - Redis password.

#### Character Service

`CHARACTER__CACHE_TTL_SECONDS` - character cache time to live in seconds. Default is `3600`.

## Development

### Global dependencies

- poetry

### Taskfile commands

For all commands see [Taskfile](Taskfile.yaml) or `task --list-all`.
