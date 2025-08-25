import requests
import urllib.parse
import argparse
import os

# https://pollinations.ai/
# https://github.com/pollinations/pollinations/blob/master/APIDOCS.md

# Get token from env
TOKEN = os.getenv("POLLINATIONS_TOKEN")

parser = argparse.ArgumentParser()
parser.add_argument("--prompt", type=str, required=True)
args = parser.parse_args()

params = {
    "token": TOKEN,
    # https://text.pollinations.ai/models
    "model": "openai",
    "seed": 100
}

optimized_prompt_request = f"Optimize the following statement: \"{args.prompt}\", replace confusing words with simpler alternatives, keep the meaning but change the wording if needed to improve clarity and conciseness, and easy understanding, and remove the surrounding environment, background."

encoded_prompt = urllib.parse.quote(optimized_prompt_request)

url = f"https://text.pollinations.ai/{encoded_prompt}"

try:
    response = requests.get(url, params=params)
    response.raise_for_status()
    print(response.text)

except requests.exceptions.RequestException as e:
    print(f"Error fetching text: {e}")
    # if response is not None: print(response.text)
