# Smart Memory

Privacy-first Telegram memory bot built with aiogram 3.31 and PostgreSQL.

## Product model

The user forwards or sends useful Telegram content to the bot. The bot copies the content into a private Telegram channel owned by the user. The application database stores only the minimum references required to retrieve that copy.

The original message body, caption, file ID, photo, video, document and other media are not persisted in PostgreSQL.

## Privacy boundary

The bot must see an incoming message to process it. This project does not claim that the bot cannot access content during processing.

The persistent application database stores:

- a pseudonymous user key derived with HMAC-SHA256
- the user's private storage channel ID
- the storage message ID
- coarse content/source metadata
- HMAC-scoped search token indexes

Raw Telegram user IDs and raw message text are not persisted.

Search token hashes are scoped by user key. The same token therefore does not produce the same database value across two users.

## Storage setup

The Telegram Bot API does not provide a bot operation for creating a channel. The user creates a private channel, adds the bot as an administrator with permission to post, and runs `/connect_storage`. The user then forwards one post from that channel to the bot. The bot verifies that the forwarded chat is a private channel and that both the bot and user are administrators.

Storage is user-owned. `/disconnect_storage` removes the application's reference to the channel. It does not delete the user's Telegram content.

## Commands

```text
/connect_storage    Connect a private storage channel
/disconnect_storage Remove the storage-channel association
/search <query>     Search indexed memories and copy matching messages back
/delete_data        Delete this service's database records for the user
```

Normal non-command messages are saved automatically after storage is configured.

## Environment

Only these variables are required by the current foundation:

```text
BOT_TOKEN=
DATABASE_URL=
PRIVACY_HASH_KEY=
```

Generate the privacy key with:

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

## Run

```bash
python -m venv .venv
.venv/bin/pip install -e '.[dev]'
cp .env.example .env
alembic upgrade head
python -m app.main
```

## Architecture

```text
Telegram
  -> aiogram handlers
  -> application services
  -> repositories
  -> PostgreSQL index

Telegram Storage Channel
  -> original user content
```

AI, embeddings and Redis are deliberately not part of the foundation. They will be added only when their data-retention and privacy model is defined and implemented.
