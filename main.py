import os
import requests
from spotipy import Spotify
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
import time  # Import the time module

# Load environment variables from .env file
load_dotenv()

# Initialize Spotify API with Client Credentials Flow
sp = Spotify(auth_manager=SpotifyClientCredentials(client_id=os.getenv('SPOTIPY_CLIENT_ID'),
                                                    client_secret=os.getenv('SPOTIPY_CLIENT_SECRET')))

# Initialize Telegram bot
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
updater = Updater(token=TELEGRAM_TOKEN, use_context=True)
dispatcher = updater.dispatcher

# Command handler to start the bot
def start(update: Update, context: CallbackContext):
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text="🎵 Welcome to the Spotify Downloader Bot! 🎵")

# Message handler to search for tracks and send download links
def search_track(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    query = update.message.text

    # Search for tracks on Spotify
    results = sp.search(q=query, type='track', limit=1)

    if results['tracks']['items']:
        track = results['tracks']['items'][0]
        track_name = track['name']
        artist_name = track['artists'][0]['name']

        # Create a temporary folder to store downloaded music
        temp_folder = f"./temp_{chat_id}"
        os.makedirs(temp_folder, exist_ok=True)
        os.chdir(temp_folder)

        # Create a download link using a service that provides 320kbps MP3
        download_link = f"https://example-download-service.com/{track_name} {artist_name} 320kbps"

        # Send the download link to Telegram
        context.bot.send_message(chat_id=chat_id, text=f"🎵 Downloading {track_name} by {artist_name}...")
        context.bot.send_message(chat_id=chat_id, text=f"🔗 Download Link: {download_link}")

        # Download the music file into the temporary folder
        response = requests.get(download_link)
        with open(f"{track_name} - {artist_name}.mp3", 'wb') as music_file:
            music_file.write(response.content)

        # Send the downloaded music to Telegram
        with open(f"{track_name} - {artist_name}.mp3", 'rb') as audio_file:
            context.bot.send_audio(chat_id=chat_id, audio=audio_file, timeout=18000)

        # Remove the temporary folder and its contents
        os.chdir('..')
        os.rmdir(temp_folder)

        # Add a delay of 0.3 seconds between sending each audio file
        sent += 1
        time.sleep(0.3)
    else:
        context.bot.send_message(chat_id=chat_id, text="❌ Track not found on Spotify.")

# Add handlers to the dispatcher
start_handler = CommandHandler('start', start)
dispatcher.add_handler(start_handler)

search_handler = MessageHandler(Filters.text & ~Filters.command, search_track)
dispatcher.add_handler(search_handler)

# Start the bot with a polling interval of 0.3 seconds
updater.start_polling(poll_interval=0.3)
updater.idle()
