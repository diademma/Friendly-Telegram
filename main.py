import os
from telethon.sync import TelegramClient

def main():
    try:
        api_id = os.getenv("API_ID")
        api_hash = os.getenv("API_HASH")
        session_string = os.getenv("SESSION")

        client = TelegramClient(session_string, api_id, api_hash)
        print("Connecting to Telegram...")
        client.connect()

        if not client.is_connected():
            print("Failed to connect. Check your API ID, API HASH, and session string.")
            return

        print("Connection successful! Getting user info...")
        me = client.get_me()
        print(f"Logged in as: @{me.username} ({me.first_name})")

    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        if 'client' in locals() and client.is_connected():
            client.disconnect()
            print("Client disconnected.")

if __name__ == "__main__":
    main()
