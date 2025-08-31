from telethon import TelegramClient, events
import os

# Берём данные из переменных окружения Railway
API_ID = int(os.environ.get("API_ID"))
API_HASH = os.environ.get("API_HASH")
SESSION = os.environ.get("SESSION"))  # строка-сессия

# Создаём клиента
client = TelegramClient(StringSession(SESSION), API_ID, API_HASH)

# Событие: когда пишешь ".ping", бот отвечает "pong"
@client.on(events.NewMessage(pattern=r"\.ping"))
async def handler(event):
    await event.reply("pong 🏓")

print("Бот запущен!")
client.start()
client.run_until_disconnected()
