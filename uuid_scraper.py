from pydantic import BaseModel
from openai import OpenAI
from dotenv import load_dotenv
import datetime
import os

from browser import *

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
time_format = "%Y-%m-%d %H:%M:%S"
base_url = "https://lecturecapture.la.utexas.edu/player/episode/"
with open("429_data.txt", "r") as f:
    html = f.read()


class VideoURL(BaseModel):
    date: list[str]
    uuid: list[str]

    def __str__(self):
        return f"VideoIDS(date={self.date}, uuid={self.uuid})"


def parse_video_urls(html) -> VideoURL:
    completion = client.beta.chat.completions.parse(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": "You are an html parser. Extract all of the UUIDS correspoding dates from the text. Return the date as python datetime string in '%Y-%m-%d %H:%M:%S', always at 1pm or 1300",
            },
            {
                "role": "user",
                "content": f"{html}",
            },
        ],
        response_format=VideoURL,
    )

    return completion.choices[0].message.parsed


video_data = parse_video_urls(html)

import json

# Create a list to hold the results
results = []

for date_str, uuid in zip(video_data.date, video_data.uuid):
    try:
        datetime_object = datetime.datetime.strptime(date_str, time_format)
        url = f"{base_url}{uuid}"
        caption_url = get_caption_url(get_html(uuid))

        # Print the information
        print(f"Date: {datetime_object}, URL: {url}")
        print(f"Caption URL: {caption_url}")
        print("\n")

        # Append results to the list
        results.append(
            {
                "date": datetime_object.strftime(time_format),
                "url": url,
                "caption_url": caption_url,
            }
        )

    except ValueError as e:
        print(f"Error parsing date string '{date_str}': {e}")
        print(f"UUID associated with the unparsable date: {uuid}")

# Write results to a JSON file
with open("video_data.json", "w") as json_file:
    json.dump(results, json_file, indent=4)
