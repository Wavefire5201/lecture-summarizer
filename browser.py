from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time
import re

base_url = "view-source:https://lecturecapture.la.utexas.edu/player/episode/"
caption_pattern = r"https://lectures-engage\.la\.utexas\.edu:443/static/mh_default_org/engage-player/[0-9A-Fa-f]{8}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{12}/[0-9A-Fa-f]{8}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{12}/laitswhisper_transcript_[0-9A-Fa-f]{8}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{12}\.vtt"

chrome_options = Options()
chrome_options.add_experimental_option("debuggerAddress", "localhost:9222")
driver = webdriver.Chrome(options=chrome_options)


def get_html(video_uuid: str) -> str:
    driver.get(f"{base_url}{video_uuid}")
    time.sleep(1)
    return driver.page_source


def get_caption_url(html: str) -> str | None:
    match = re.findall(caption_pattern, html)
    if match:
        return match[0]
    return None
