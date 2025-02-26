import requests
import json
import os

os.makedirs("captions", exist_ok=True)

with open("video_data.json", "r") as f:
    video_data = json.load(f)


def download_captions(caption_url, output_file):
    response = requests.get(caption_url)
    if response.status_code == 200:
        with open(output_file, "wb") as f:
            f.write(response.content)
        print(f"Downloaded: {output_file}")
    else:
        print(f"Failed to download: {caption_url}")


for video in video_data:
    caption_url = video["caption_url"]
    if caption_url:
        output_file = f"captions/{video['uuid']}.vtt"
        download_captions(caption_url, output_file)
    else:
        print(f"No caption URL for video on {video['date']}")
