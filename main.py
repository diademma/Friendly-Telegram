from telethon import TelegramClient, events
from telethon.sessions import StringSession
import os
import smtplib
from email.message import EmailMessage

# --- Настройки ---
API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
SESSION = os.getenv("SESSION")

EMAIL_USER = os.getenv("EMAIL_USER")   # твой email (ukr.net)
EMAIL_PASS = os.getenv("EMAIL_PASS")   # пароль приложения от ukr.net
EMAIL_TO = os.getenv("EMAIL_TO")       # куда слать (твой же email)

# Каналы для мониторинга
CHANNELS = [
    "https://t.me/foma_sinitsaa",
    "https://t.me/FunWednesday",
    "https://t.me/rand2ch",
    "https://t.me/MemDoze",
    "https://t.me/spotsonthesuns",
    "https://t.me/luka_lisitsa",
    "https://t.me/nononopleaseno",
    "https://t.me/no_fucken_hope",
    "https://t.me/OneESTET",
    "https://t.me/stpetersburg_escort",
    "https://t.me/opjat_ne_spitsa"
]

client = TelegramClient(StringSession(SESSION), API_ID, API_HASH)

# --- Функция отправки email ---
def send_email(file_path, file_name):
    try:
        msg = EmailMessage()
        msg["From"] = EMAIL_USER
        msg["To"] = EMAIL_TO
        msg["Subject"] = f"Новый файл из Telegram: {file_name}"

        with open(file_path, "rb") as f:
            msg.add_attachment(f.read(),
                               maintype="application",
                               subtype="octet-stream",
                               filename=file_name)

        with smtplib.SMTP_SSL("smtp.ukr.net", 465) as server:
            server.login(EMAIL_USER, EMAIL_PASS)
            server.send_message(msg)
        print(f"[OK] Отправлено: {file_name}")
    except Exception as e:
        print(f"[ERR] {e}")

# --- Обработчик новых сообщений ---
@client.on(events.NewMessage(chats=CHANNELS))
async def handler(event):
    if event.media:
        file = await event.download_media()
        size_mb = os.path.getsize(file) / (1024 * 1024)

        if size_mb <= 23:
            send_email(file, os.path.basename(file))
        else:
            print(f"[SKIP] {os.path.basename(file)} слишком большой ({size_mb:.1f} MB)")

# --- Запуск ---
print("Бот запущен...")
client.start()
client.run_until_disconnected()
