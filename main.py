import os
import asyncio
import logging
from telethon import TelegramClient, events
from telethon.sessions import StringSession
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.utils import formatdate
from email import encoders
import smtplib
import time
from http.server import HTTPServer, BaseHTTPRequestHandler
from threading import Thread

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# --- Environment Variables ---
# Replit будет брать эти данные из раздела "Secrets".
# API_ID должен быть числом, поэтому используем int().
API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
SESSION = os.getenv("SESSION")
EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASS = os.getenv("EMAIL_PASS")
EMAIL_TO = os.getenv("EMAIL_TO")

# --- SMTP Configuration ---
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
MAX_EMAIL_SIZE_MB = 23
MAX_EMAIL_SIZE_BYTES = MAX_EMAIL_SIZE_MB * 1024 * 1024

# List of channels to monitor
CHANNELS = [
    'https://t.me/foma_sinitsaa',
    'https://t.me/FunWednesday',
    'https://t.me/rand2ch',
    'https://t.me/MemDoze',
    'https://t.me/spotsonthesuns',
    'https://t.me/luka_lisitsa',
    'https://t.me/nononopleaseno',
    'https://t.me/no_fucken_hope',
    'https://t.me/OneESTET',
    'https://t.me/stpetersburg_escort',
    'https://t.me/opjat_ne_spitsa',
    'https://t.me/tio_like_this'
]

# --- Global storage for files ---
files_to_send = {
    'photos': {},
    'videos': {}
}
# Time limit for sending files
SEND_TIMEOUT_SECONDS = 300 # 5 minutes

# --- Email Sending Function ---
async def send_email(subject, body, file_paths):
    """Sends an email with a list of attachments."""
    msg = MIMEMultipart()
    msg['From'] = EMAIL_USER
    msg['To'] = EMAIL_TO
    msg['Date'] = formatdate(localtime=True)
    msg['Subject'] = subject

    msg.attach(MIMEBase('text', 'plain'))
    msg.get_payload()[0].set_payload(body)

    for filepath in file_paths:
        filename = os.path.basename(filepath)
        part = MIMEBase('application', 'octet-stream')
        try:
            with open(filepath, 'rb') as file:
                part.set_payload(file.read())
            encoders.encode_base64(part)
            part.add_header('Content-Disposition', f'attachment; filename="{filename}"')
            msg.attach(part)
        except FileNotFoundError:
            logging.error(f"File not found: {filepath}")
            continue

    try:
        logging.info(f"Connecting to SMTP server at {SMTP_SERVER}...")
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(EMAIL_USER, EMAIL_PASS)
        logging.info("SMTP login successful. Sending email...")
        server.send_message(msg)
        server.quit()
        logging.info("Email sent successfully!")
        return True
    except Exception as e:
        logging.error(f"Failed to send email: {e}")
        return False

# --- New coroutine to handle scheduled emails ---
async def send_scheduled_emails():
    while True:
        await asyncio.sleep(60) # Check every minute
        
        # Process photos
        for channel, files in list(files_to_send['photos'].items()):
            current_size = sum(f['size'] for f in files)
            if len(files) >= 6 or (time.time() - files[0]['timestamp'] > SEND_TIMEOUT_SECONDS and len(files) > 0) or current_size >= MAX_EMAIL_SIZE_BYTES * 0.9:
                logging.info(f"Sending batch of {len(files)} photos from channel {channel}")
                file_paths = [f['path'] for f in files]
                subject = f"Photos from {channel}"
                body = f"Photos from {channel}"
                await send_email(subject, body, file_paths)
                for f in file_paths:
                    if os.path.exists(f):
                        os.remove(f)
                del files_to_send['photos'][channel]

        # Process videos
        for channel, files in list(files_to_send['videos'].items()):
            current_size = sum(f['size'] for f in files)
            if len(files) >= 2 or (time.time() - files[0]['timestamp'] > SEND_TIMEOUT_SECONDS and len(files) > 0) or current_size >= MAX_EMAIL_SIZE_BYTES * 0.9:
                logging.info(f"Sending batch of {len(files)} videos from channel {channel}")
                file_paths = [f['path'] for f in files]
                subject = f"Videos from {channel}"
                body = f"Videos from {channel}"
                await send_email(subject, body, file_paths)
                for f in file_paths:
                    if os.path.exists(f):
                        os.remove(f)
                del files_to_send['videos'][channel]

# --- Web Server for Pinger ---
# Replit требует, чтобы приложение запускало веб-сервер, иначе оно "заснёт".
class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(b"Bot is active!")

def run_server():
    # Replit предоставляет порт через переменную окружения
    server_address = ('', int(os.environ.get('PORT', 8080)))
    httpd = HTTPServer(server_address, SimpleHTTPRequestHandler)
    logging.info(f"Web server started on port {os.environ.get('PORT', 8080)}")
    httpd.serve_forever()

# --- Telegram Bot Logic ---
client = TelegramClient(StringSession(SESSION), API_ID, API_HASH)

@client.on(events.NewMessage(chats=CHANNELS))
async def handle_new_message(event):
    if event.media and (hasattr(event.media, 'document') or hasattr(event.media, 'photo')):
        file_size = None
        file_type = None

        if hasattr(event.media, 'document'):
            file_size = event.media.document.size
            if event.media.document.mime_type.startswith("video"):
                file_type = "videos"
            else:
                file_type = "photos" # Treat other documents as photos for now
        elif hasattr(event.media, 'photo'):
            # Находим самый большой размер фотографии, чтобы получить её размер
            largest_size_obj = max(
                (s for s in event.media.photo.sizes if hasattr(s, 'size')),
                key=lambda s: s.size,
                default=None
            )
            if largest_size_obj:
                file_size = largest_size_obj.size
                file_type = "photos"
            else:
                logging.info("Skipping photo with no 'size' attribute in any variant.")
                return

        if file_size is None or file_type is None:
            logging.info("Skipping media with no recognizable size or type.")
            return

        # Check if the file is too big for a single email
        if file_size > MAX_EMAIL_SIZE_BYTES:
            logging.warning(f"File skipped. Size ({file_size / (1024*1024):.2f} MB) exceeds the {MAX_EMAIL_SIZE_MB} MB limit.")
            return

        # Get channel name from peer
        channel = await client.get_entity(event.peer_id)
        channel_username = f"https://t.me/{channel.username}" if channel.username else f"Channel ID: {channel.id}"

        # Download the file
        file_path = await client.download_media(event.media)

        # Add file to our global queue
        if channel_username not in files_to_send[file_type]:
            files_to_send[file_type][channel_username] = []

        files_to_send[file_type][channel_username].append({
            'path': file_path,
            'size': file_size,
            'timestamp': time.time()
        })
        
        logging.info(f"Added new {file_type[:-1]} from {channel_username} to queue. Current queue size: {len(files_to_send[file_type][channel_username])}")

# --- Main Logic ---
async def main():
    if not all([API_ID, API_HASH, SESSION, EMAIL_USER, EMAIL_PASS, EMAIL_TO]):
        logging.error("One or more required variables are missing. Please fill them in the 'Secrets' menu.")
        return

    # Запускаем веб-сервер в отдельном потоке, чтобы бот не "заснул".
    server_thread = Thread(target=run_server)
    server_thread.daemon = True
    server_thread.start()

    logging.info("Starting Telegram userbot...")
    try:
        await client.start()
        
        # Запускаем отправку почты в фоновом режиме
        asyncio.create_task(send_scheduled_emails())
        
        logging.info("Bot is running. Listening for new messages...")
        await client.run_until_disconnected()
    except Exception as e:
        logging.error(f"Failed to start bot: {e}")

if __name__ == "__main__":
    asyncio.run(main())
