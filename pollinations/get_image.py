import requests
import urllib.parse
import argparse
import re
import os
from PIL import Image
from io import BytesIO

# https://pollinations.ai/
# https://github.com/pollinations/pollinations/blob/master/APIDOCS.md

# Get token from env
TOKEN = os.getenv("POLLINATIONS_TOKEN")

parser = argparse.ArgumentParser()
parser.add_argument("-p", "--prompt", type=str, required=True)
parser.add_argument("-fp", "--filename_prefix", type=str, default="")
args = parser.parse_args()

RESULT_FOLDER = "results"

custom_prompt = f"{args.prompt}, set against a uniformly colored background with high contrast to the object’s color. Avoid background colors that are too bright or too dark; the background should differ significantly from the object to make it easy to remove the background later. The object should absorb light well, without small reflective spots. It must not have missing, overly detailed, or unappealing parts, and should match the description. Render the entire full body of the object within the frame, viewed from an isometric angle at 45 degrees from the front and above, angled downward. Keep the design simple with clean, detailed features."

encoded_prompt = urllib.parse.quote(custom_prompt)

params = {
    "token": TOKEN,
    "width": 1024,
    "height": 1024,
    "seed": 100,
    "model": "flux",
    "nologo": "true", # Optional, set to "true" for registered referrers/tokens
    # "image": "https://example.com/input-image.jpg", # Optional - for image-to-image generation (kontext model)
    # "referrer": "MyPythonApp" # Optional for referrer-based authentication
}

url = f"https://image.pollinations.ai/prompt/{encoded_prompt}"

try:
    print(f"Generating image...")
    print(f"Prompt: {custom_prompt}")
    response = requests.get(url, params=params, timeout=300) # Increased timeout for image generation
    response.raise_for_status() # Raise an exception for bad status codes

    file_path = args.filename_prefix + "_" + re.sub(r'[^a-zA-Z0-9]', '_', custom_prompt.strip())[:200]

    print(f"Saving image to {RESULT_FOLDER}")
    os.makedirs(RESULT_FOLDER, exist_ok=True)
    Image.open(BytesIO(response.content)).save(f"{RESULT_FOLDER}/{file_path}.png", "png")

except requests.exceptions.RequestException as e:
    print(f"Error fetching image: {e}")
    # Consider checking response.text for error messages from the API
    # if response is not None: print(response.text)
