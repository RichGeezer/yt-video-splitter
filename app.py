import streamlit as st
from yt_dlp import YoutubeDL
from moviepy.editor import VideoFileClip
import os
import tempfile

st.title("YouTube Video Splitter")

yt_url = st.text_input("Paste YouTube video URL here:")

clip_length = st.slider("Clip length (seconds)", min_value=30, max_value=300, value=90, step=10)

if yt_url and st.button("Download and Split"):
    with st.spinner("Downloading video..."):
        temp_dir = tempfile.mkdtemp()
        ydl_opts = {
            "format": "mp4",
            "outtmpl": os.path.join(temp_dir, "video.%(ext)s"),
            "quiet": True,
            "no_warnings": True,
        }
        try:
            with YoutubeDL(ydl_opts) as ydl:
                ydl.download([yt_url])
        except Exception as e:
            st.error(f"Error downloading video: {e}")
            st.stop()

    video_path = os.path.join(temp_dir, "video.mp4")
    if not os.path.exists(video_path):
        # Sometimes extension can vary, find mp4 in temp_dir
        files = os.listdir(temp_dir)
        for f in files:
            if f.endswith(".mp4"):
                video_path = os.path.join(temp_dir, f)
                break

    st.success("Download complete!")

    video = VideoFileClip(video_path)
    duration = int(video.duration)
    st.write(f"Video duration: {duration} seconds")

    clips = []
    for start in range(0, duration, clip_length):
        end = min(start + clip_length, duration)
        clip = video.subclip(start, end)
        clip_file = os.path.join(temp_dir, f"clip_{start}_{end}.mp4")
        clip.write_videofile(clip_file, codec="libx264", audio_codec="aac", verbose=False, logger=None)
        clips.append((clip_file, start, end))

    st.success(f"Created {len(clips)} clips")

    for idx, (clip_file, start, end) in enumerate(clips):
        st.video(clip_file)
        st.write(f"Clip {idx+1}: {start} s to {end} s")

    video.close()
