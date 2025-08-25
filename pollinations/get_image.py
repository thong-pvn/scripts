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
parser.add_argument("--prompt", type=str, required=True)
parser.add_argument("--filename_prefix", type=str, default="")
args = parser.parse_args()

RESULT_FOLDER = "results"

custom_prompt = args.prompt + ", in huge black space, toy-like appearance. It is fresh-color, non reflective, solid texture, opaque fabric. It is a game asset. It has a smooth, stylized, low-poly design, with minimalist details and rounded edges. It is isometric view, (45-degree/45-degree) camera angle. The main color for the parts that are not clearly described will be red."
# custom_prompt = args.prompt + ", no background, no watermark, whole body, full body in view, isometric view, (45-degree/45-degree) camera angle"

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
