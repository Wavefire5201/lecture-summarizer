import requests
from bs4 import BeautifulSoup

# URL of the webpage containing the HTML snippet
webpage_url = "https://example.com"  # Replace with the actual URL

# Fetch the webpage content
response = requests.get(webpage_url)
if response.status_code == 200:
    html_content = response.text

    # Parse the HTML using BeautifulSoup
    soup = BeautifulSoup(html_content, 'html.parser')

    # Locate the <track> element with kind="captions"
    track_element = soup.find('track', {'kind': 'captions'})

    if track_element:
        # Extract the caption URL from the 'src' attribute
        caption_url = track_element.get('src')
        print("Caption URL:", caption_url)

        # If the caption URL is relative, construct the full URL
        if caption_url.startswith('/'):
            base_url = response.url.rsplit('/', 1)[0]
            caption_url = base_url + caption_url
        
        # Fetch and display the captions
        captions_response = requests.get(caption_url)
        if captions_response.status_code == 200:
            print("Captions Content:")
            print(captions_response.text)
        else:
            print("Failed to fetch captions.")
    else:
        print("No caption track found.")
else:
    print("Failed to fetch webpage.")

