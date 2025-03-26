
import streamlit as st
from moviepy.editor import VideoFileClip
import os
import yt_dlp as youtube_dl
from pathlib import Path

def get_download_folder():
    """Returns the default Downloads folder path based on the OS."""
    return str(Path.home() / "Downloads")

def download_video(url):
    """Downloads a video from a given URL and returns its file path."""
    download_folder = get_download_folder()
    ydl_opts = {
        "outtmpl": os.path.join(download_folder, "%(title)s.%(ext)s"),
        "format": "best",
    }

    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        info_dict = ydl.extract_info(url, download=True)
        video_path = ydl.prepare_filename(info_dict)  # Path to the downloaded video
    return video_path

def split_video(input_video_path, clip_duration=120):
    """Splits a video into clips of the specified duration and saves them in Downloads folder."""
    video = VideoFileClip(input_video_path)
    video_duration = video.duration
    
    output_dir = get_download_folder()  # Save clips directly in Downloads folder
    clip_number = 1
    clip_paths = []

    for start_time in range(0, int(video_duration), clip_duration):
        end_time = min(start_time + clip_duration, video_duration)
        clip = video.subclip(start_time, end_time)
        clip_path = os.path.join(output_dir, f"clip_{clip_number}.mp4")
        clip.write_videofile(clip_path, codec="libx264", audio_codec="aac")
        clip_paths.append(clip_path)
        clip_number += 1
    
    return clip_paths

# Streamlit UI
st.title("Video Downloader & Splitter")
st.write("Enter a video URL (e.g., YouTube), and it will be downloaded and split into clips of specified duration.")

video_url = st.text_input("Enter Video URL")
clip_duration = st.text_input("Enter Clip Duration (in seconds)")
if clip_duration.strip():
    clip_duration = int(clip_duration)
else:
    st.error("Clip duration cannot be empty.")

if video_url:
    if st.button("Download and Split Video"):
        with st.spinner("Downloading the video..."):
            try:
                video_path = download_video(video_url)
                st.success(f"Video downloaded successfully! Saved in Downloads folder: {video_path}")
                
                with st.spinner("Splitting the video into clips..."):
                    clip_paths = split_video(video_path, clip_duration)
                
                st.success("Video split successfully! Clips saved in Downloads folder.")
                
                for clip_path in clip_paths:
                    with open(clip_path, "rb") as file:
                        st.download_button(
                            label=f"Download {os.path.basename(clip_path)}",
                            data=file,
                            file_name=os.path.basename(clip_path),
                            mime="video/mp4"
                        )

            except Exception as e:
                st.error(f"An error occurred: {e}")

