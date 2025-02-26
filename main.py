import yt_dlp
import streamlit as st
import os
import re

# Helper functions


def is_valid_uuid(uuid):
    regex = re.compile(
        r"^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$"
    )
    return re.match(regex, uuid) is not None


def get_url(uuid):
    return f"https://streaming-lectures.la.utexas.edu/lo/smil:engage-player_{uuid}_presentation.smil/chunklist_b207817.m3u8"


def download_video(url, output_path):
    ydl_opts = {
        "outtmpl": output_path,  # Specify the output path and filename for the downloaded video
        "format": "best",  # Download the best quality video available
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])


# Begin app

st.title("Lectures Online Summarizer")

uuid = st.text_input("Video UUID").lower()
confirm = st.button("Confirm")


video_url = get_url(uuid)
output_path = f"lectures/{uuid}.mp4"

if confirm and is_valid_uuid(uuid):
    if not os.path.exists(output_path):
        with st.spinner("Video is downloading..."):
            download_video(video_url, output_path)

    st.video(output_path, "video/mp4")
elif not is_valid_uuid(uuid):
    st.error("Please enter a valid UUID.")
