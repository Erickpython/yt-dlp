import os
import streamlit as st
import yt_dlp


st.set_page_config(
    page_title = "YouTube Playlist Downloader",
    page_icon = ":arrow_down:", 
    layout="centered")

st.title ("YouTube Playlist Downloader")
st.write("Download entire YouTube playlists as MP3 or MP4 files.")

#input
playlist_url = st.text_input("Enter YouTube Playlist URL: ")

#choose format
option = st.radio("Choose Download Format:", ("Audio (MP3)", "Video (MP4)"))

#progress
progress_bar = st.progress(0)
progress_text = st.empty()
summary_box = st.empty()

# create downloads directory 
os.makedirs('downloads', exist_ok=True)

#Download archive to track completed downloads
archive_file = 'downloads/downloaded_videos.txt'


def progress_hook(d):
    """Update progress bar based on download status."""
    if d['status'] == 'downloading':
        percent = d.get('_percent_str', '0.0%')
        filename = d.get('filename', '...')
        progress_text.text (f"Downloading: {os.path.basename(filename)} - {percent}")
        try:
            #converting decimal percentages
            progress_value = float(percent.replace('%', '')).strip()
            progress_bar.progress(min(int(progress_value), 100))
        except:
            pass

    elif d['status'] == 'finished':
        progress_text.text("Download completed, finalizing...")
        progress_bar.progress(100)

def get_playlist_info(url):
    """Fetch playlist information using yt_dlp."""
    ydl_opts = {
        'skip_download': True,
        'extract_flat': True,
        'dump_single_json': True,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
    return info

#download button
if st.button("Download Playlist"):
    if not playlist_url:
        st.warning("Please enter a YouTube playlist URL.")
    else:
        try:
            info = get_playlist_info(playlist_url)
            playlist_title = info.get('title', 'Unknown Playlist')
            video_count = len(info.get('entries', []))
            summary_box.info(f"Playlist: **{playlist_title}** - {video_count} videos found.")

            st.info("Starting downloading... This may take a while for large playlists.")

            # yt-dlp options
            if option == "Video (MP4)":
                ydl_opts = {
                    'format': 'bestvideo+bestaudio/best',
                    'outtmpl': 'downloads/%(playlist_title)s/%(title)s.%(ext)s',
                    'merge_output_format': 'mp4',
                    'progress_hooks': [progress_hook],
                    'download_archive': archive_file,
                    'noplaylist': False,
                    'overwrites': False,
                    'cookiefile': 'cookies.txt'  # Use cookies for age-restricted content
                }

            else:  # Audio (MP3)
                ydl_opts = {
                    'format': 'bestaudio/best',
                    'outtmpl': 'downloads/%(playlist_title)s/%(title)s.%(ext)s',
                    'postprocessors': [{
                        'key': 'FFmpegExtractAudio',
                        'preferredcodec': 'mp3',
                        'preferredquality': '192',
                    }],
                    'progress_hooks': [progress_hook],
                    'download_archive': archive_file,
                    'noplaylist': False,
                    'overwrites': False,
                    'cookiefile': 'cookies.txt'  
                }


            # Start downloading
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([playlist_url])

            progress_text.text("All downloads completed!")
            progress_bar.progress(100)
            st.success("All downloads completed!")

        except Exception as e:
            st.error(f"An error occurred: {e}")
