import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from pytube import YouTube, Search
import os
import time
import concurrent.futures
from dotenv import load_dotenv

load_dotenv()


def download_song(song_info):
    video_id = song_info["video_id"]
    playlist_name = song_info["playlist_name"]
    song_name = song_info["song_name"]

    try:
        yt = YouTube(f'https://www.youtube.com/watch?v={video_id}')
        try:
            audio = yt.streams.get_audio_only()
            try:
                download_file = audio.download(output_path=playlist_name)
                file_name, ext = os.path.splitext(download_file)
                new_file = file_name + ".mp3"
                os.rename(download_file, new_file)
            except Exception as download_error:
                print(f"Error in download for '{song_name}': {download_error}")
        except Exception as audio_error:
            print(f"Error in audio stream for '{song_name}': {audio_error}")
    except Exception as youtube_error:
        print(f"Error in YouTube video ID for '{song_name}': {youtube_error}")


def search_song(song_name, artist, playlist_name):
    try:
        search_results = Search(f"{song_name} {artist}")
        if search_results:
            video_id_result = search_results.results[0].video_id
            return {
                "video_id": video_id_result,
                "playlist_name": playlist_name,
                "song_name": song_name
            }
        else:
            print(f"No search results found for '{song_name}'")
            return None
    except Exception as search_error:
        print(f"Error in search for '{song_name}': {search_error}")
        return None


def search_and_download(song_info):
    song_name = song_info["song_name"]
    artist = song_info["artist"]
    playlist_name = song_info["playlist_name"]

    video_id = search_song(song_name, artist, playlist_name)
    if video_id:
        download_song(video_id)


def main(playlist_link):
    seen_song_name = set()
    filtered_list = []

    # Authentication - without user
    client_credentials_manager = SpotifyClientCredentials(client_id=os.getenv('CLIENT_ID'),
                                                          client_secret=os.getenv('CLIENT_SECRET'))
    sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

    playlist_uri = playlist_link.split("/")[-1].split("?")[0]
    playlist = sp.playlist(playlist_uri)
    playlist_name = playlist['name']

    for item in playlist["tracks"]["items"]:
        song_name = item["track"]["name"]
        artist = item["track"]["artists"][0]["name"]
        if song_name not in seen_song_name:
            seen_song_name.add(song_name)
            filtered_list.append({
                "song_name": song_name,
                "artist": artist,
                "playlist_name": playlist_name
            })

    start_time = time.time()  # Record start time

    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = [executor.submit(search_and_download, song) for song in filtered_list]

    # Wait for all tasks to complete
    concurrent.futures.wait(futures)

    end_time = time.time()  # Record end time
    execution_time = end_time - start_time
    print(f"Execution time: {execution_time:.2f}")


if __name__ == "__main__":
    link = ""
    main(link)
