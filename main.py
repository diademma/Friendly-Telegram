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

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Environment variables
API_ID = os.getenv("API_ID")
API_HASH = os.getenv("API_HASH")
SESSION = os.getenv("SESSION")
EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASS = os.getenv("EMAIL_PASS")
EMAIL_TO = os.getenv("EMAIL_TO")

# --- SMTP Configuration ---
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
MAX_FILE_SIZE_MB = 23

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
    'https://t.me/opjat_ne_spitsa'
]

# --- Email Sending Function ---
async def send_email(subject, body, filename=None, filepath=None):
    """Sends an email with an optional attachment."""
    msg = MIMEMultipart()
    msg['From'] = EMAIL_USER
    msg['To'] = EMAIL_TO
    msg['Date'] = formatdate(localtime=True)
    msg['Subject'] = subject

    msg.attach(MIMEBase('text', 'plain'))
    msg.get_payload()[0].set_payload(body)

    if filename and filepath:
        part = MIMEBase('application', 'octet-stream')
        try:
            with open(filepath, 'rb') as file:
                part.set_payload(file.read())
            encoders.encode_base64(part)
            part.add_header('Content-Disposition', f'attachment; filename="{filename}"')
            msg.attach(part)
        except FileNotFoundError:
            logging.error(f"File not found: {filepath}")
            return

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

# --- Telegram Bot Logic ---
client = TelegramClient(StringSession(SESSION), API_ID, API_HASH)

@client.on(events.NewMessage(chats=CHANNELS))
async def handle_new_message(event):
    """Handles new messages with media."""
    if event.media and event.media.document:
        file_size_mb = event.media.document.size / (1024 * 1024)
        file_name = event.media.document.attributes[0].file_name if event.media.document.attributes else 'unknown_file'

        logging.info(f"New media message detected. File: {file_name}, Size: {file_size_mb:.2f} MB")

        if file_size_mb <= MAX_FILE_SIZE_MB:
            logging.info(f"File size is within the limit. Downloading {file_name}...")
            
            try:
                file_path = await client.download_media(event.media)
                
                subject = f"Telegram Media Forward: {file_name}"
                body = f"The following media file was forwarded from Telegram:\n\nFile Name: {file_name}\nFile Size: {file_size_mb:.2f} MB"
                
                success = await send_email(subject, body, filename=file_name, filepath=file_path)
                
                if success:
                    logging.info(f"Successfully forwarded {file_name} to email.")
                
                os.remove(file_path)
                logging.info(f"Removed temporary file: {file_path}")

            except Exception as e:
                logging.error(f"An error occurred during download or email sending: {e}")
        else:
            logging.warning(f"File {file_name} skipped. Size ({file_size_mb:.2f} MB) exceeds the {MAX_FILE_SIZE_MB} MB limit.")

# --- Main Logic ---
async def main():
    """Main function to run the bot."""
    if not all([API_ID, API_HASH, SESSION, EMAIL_USER, EMAIL_PASS, EMAIL_TO]):
        logging.error("One or more environment variables are missing. Please check your Railway configuration.")
        return

    logging.info("Starting Telegram userbot...")
    try:
        await client.start()
        
        logging.info("Bot is running. Listening for new messages...")
        await client.run_until_disconnected()
    except Exception as e:
        logging.error(f"Failed to start bot: {e}")

if __name__ == "__main__":
    asyncio.run(main())
