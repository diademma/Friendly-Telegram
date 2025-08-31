import os
import asyncio
from telethon import TelegramClient, events

# Данные из Railway Variables
API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
SESSION = os.getenv("SESSION")

# Список каналов для отслеживания
channels = [
    "@foma_sinitsaa",
    "@FunWednesday",
    "@rand2ch",
    "@MemDoze",
    "@spotsonthesuns",
    "@luka_lisitsa",
    "@nononopleaseno",
    "@no_fucken_hope",
    "@OneESTET",
    "@stpetersburg_escort",
    "@opjat_ne_spitsa"
]

# Создаём клиент
client = TelegramClient(StringSession(SESSION), API_ID, API_HASH)

@client.on(events.NewMessage(chats=channels))
async def handler(event):
    if event.photo:
        size = event.photo.sizes[-1].size if hasattr(event.photo, 'sizes') else 0
        if size <= 23 * 1024 * 1024:
            print(f"Нашёл фото в {event.chat.username or event.chat_id} → Отправил бы на почту")
        else:
            print(f"Фото слишком большое ({size/1024/1024:.2f}MB) → Пропущено")

    elif event.video:
        if event.file.size <= 23 * 1024 * 1024:
            print(f"Нашёл видео в {event.chat.username or event.chat_id} ({event.file.size/1024/1024:.2f}MB) → Отправил бы на почту")
        else:
            print(f"Видео слишком большое ({event.file.size/1024/1024:.2f}MB) → Пропущено")

async def main():
    print("Бот запущен и слушает каналы...")
    await client.run_until_disconnected()

if __name__ == "__main__":
    with client:
        client.loop.run_until_complete(main())
