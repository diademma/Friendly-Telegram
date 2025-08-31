import os
from telethon import TelegramClient
from telethon.sessions import StringSession

API_ID = int(os.environ.get("API_ID"))
API_HASH = os.environ.get("API_HASH")
SESSION = os.environ.get("SESSION")  # строка-сессия

client = TelegramClient(StringSession(SESSION), API_ID, API_HASH)

async def main():
    me = await client.get_me()
    print("Бот запущен как:", me.username)

with client:
    client.loop.run_until_complete(main())
