from pydantic import BaseModel
from openai import OpenAI
from dotenv import load_dotenv
import datetime
import os
import json
from pypdf import PdfReader

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


class LectureNote(BaseModel):
    title: str
    date: str
    notes: str

    def __str__(self):
        return f"LectureNote(title={self.title}, date={self.date}, notes={self.notes})"


def parse_video_urls(html: str) -> VideoURL | None:
    completion = client.beta.chat.completions.parse(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": "You are an html parser. Extract all of the UUIDS corresponding dates from the text. Return the date as python datetime string in '%Y-%m-%d %H:%M:%S', always at 1pm or 1300",
            },
            {
                "role": "user",
                "content": f"{html}",
            },
        ],
        response_format=VideoURL,
    )
    return completion.choices[0].message.parsed


def save_video_data(video_data: VideoURL, filename: str) -> None:
    if video_data:
        results = []
        for date_str, uuid in zip(video_data.date, video_data.uuid):
            try:
                datetime_object = datetime.datetime.strptime(date_str, time_format)
                url = f"{base_url}{uuid}"
                caption_url = get_caption_url(get_html(uuid))
                print(f"Date: {datetime_object}, URL: {url}")
                print(f"Caption URL: {caption_url}")
                results.append(
                    {
                        "uuid": uuid,
                        "date": datetime_object.strftime(time_format),
                        "url": url,
                        "caption_url": caption_url,
                    }
                )
            except ValueError as e:
                print(f"Error parsing date string '{date_str}': {e}")
                print(f"UUID associated with the unparsable date: {uuid}")
        with open(filename, "w") as json_file:
            json.dump(results, json_file, indent=4)
    else:
        print("No video data found.")


# save_video_data(parse_video_urls(html), "video_data.json")

# run to start the browser
# google-chrome-stable --remote-debugging-port=9222 --user-data-dir="/home/wavefire/.config/google-chrome"


def create_notes(filename: str):
    with open(filename, "r") as f:
        video_data = json.load(f)

    for video in video_data:
        try:
            caption_file = f"captions/{video['uuid']}.vtt"
            pdf_file = f"pdfs/{video['uuid']}.pdf"
            output_file = f"notes/{video['date']}.md"

            if os.path.exists(output_file):
                print(f"Skipping {video['date']} - notes already exist")
                continue

            if not os.path.exists(caption_file) or not os.path.exists(pdf_file):
                print(f"Missing files for {video['date']}, skipping...")
                continue
            print(f"Creating notes for {video['date']}")

            with open(caption_file, "r") as f:
                captions = f.read()
            pdf_data = ""
            reader = PdfReader(pdf_file)
            for i, page in enumerate(reader.pages):
                pdf_data += f"Start Page {i + 1}:\n"
                pdf_data += page.extract_text()
                pdf_data += f"\nEnd Page {i + 1}:\n"

            print(
                f"Processing {len(pdf_data)} characters of PDF data and {len(captions)} characters of caption data."
            )
            print(
                f"PDF data: {pdf_data[:100]}..."
            )  # Print the first 100 characters of PDF data
            print(
                f"Caption data: {captions[:100]}..."
            )  # Print the first 100 characters of caption data

            try:
                completion = client.beta.chat.completions.parse(
                    model="gpt-4o-mini",
                    messages=[
                        {
                            "role": "system",
                            "content": """
                            You are an AI language model skilled at taking detailed, concise, succinct, and easy-to-understand notes on various subjects in bullet-point advanced markdown format. When provided with a passage or a topic, your task is to:
                            -Create advanced bullet-point notes summarizing the important parts of the reading or topic.
                            -Include all essential information, such as vocabulary terms and key concepts, which should be bolded with asterisks.
                            -Remove any extraneous language, focusing only on the critical aspects of the passage or topic.
                            -Strictly base your notes on the provided text, without adding any external information.
                            """,
                        },
                        {
                            "role": "user",
                            "content": f"""
                            I have a transcript of my lecture and the slides that goes with it. Make a comprehensive and detailed notes document in markdown to fully capture the ideas taught in this lecture. Make sure to not leave any information and expand on any information if needed. The title and first line should be in the format of "# Lecture Topic - Date"

                            Caption Data: {captions}
                            PDF Data: {pdf_data}
                            """,
                        },
                    ],
                    response_format=LectureNote,
                )

                os.makedirs("notes", exist_ok=True)
                with open(output_file, "w") as f:
                    f.write(completion.choices[0].message.parsed.notes)
                    print(f"Successfully created notes for {video['date']}")

            except Exception as e:
                print(f"Error creating notes for {video['date']}: {e}")

        except Exception as e:
            print(f"Error processing {video.get('date', 'unknown date')}: {e}")


def rename_pdfs():
    files = []
    with open("video_data.json", "r") as f:
        video_data = json.load(f)

    for filename in os.listdir("pdfs"):
        files.append(filename)
    files.sort()

    for i, filename in enumerate(files):
        if i < len(video_data):
            os.rename(f"pdfs/{filename}", f"pdfs/{video_data[i]['uuid']}.pdf")


create_notes("429_exam1.json")
