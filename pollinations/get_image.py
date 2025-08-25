import argparse
import pollinations
import re
import os

# https://pollinations.ai/

# DEFAULT_NEGATIVE_PROMPT = "extra objects, logo, watermark, background scene, ugly, bad anatomy, blurry, pixelated obscure, unnatural colors, poor lighting, dull, and unclear, cropped, lowres, low quality, artifacts, duplicate, morbid, mutilated, poorly drawn face, deformed, dehydrated, bad proportions, shadow, lack of light, dark shadows, uneven lighting, harsh shadows, low light, poorly lit, overexposed, inconsistent illumination, one side dark, high contrast lighting, noisy background"

DEFAULT_NEGATIVE_PROMPT = ""

# green_tea_bag_in_cup_steeping_liquid,no_backgound,_whole_body,_no_watermark,full_body_in_view,isometric_view

parser = argparse.ArgumentParser()
parser.add_argument("--prompt", type=str, required=True)
parser.add_argument("--negative_prompt", type=str, default=DEFAULT_NEGATIVE_PROMPT)
parser.add_argument("--filename_prefix", type=str, default="")
args = parser.parse_args()

RESULT_FOLDER = "results"

model = pollinations.Image(
    # https://image.pollinations.ai/models
    model="flux",
    width=1024,
    height=1024,
    seed=100,
    nologo=True,
)

custom_prompt = args.prompt + ", no background, no watermark, whole body, full body in view, isometric view, (45-degree/45-degree) camera angle"
# custom_prompt = "A " + args.prompt + ", floating in black space, toy-like appearance. It is fresh-color, non reflective, solid texture, opaque fabric. It is a game asset. It has a smooth, stylized, low-poly design, with minimalist details and rounded edges."

print(f"Generating image...")
print(f"Prompt: {custom_prompt}")
print(f"Negative prompt: {args.negative_prompt}")

image = model.Generate(
    prompt=custom_prompt,
    negative_prompt=args.negative_prompt
)

file_path = args.filename_prefix + "_" + re.sub(r'[^a-zA-Z0-9]', '_', custom_prompt.strip())[:200]

print(f"Saving image to {RESULT_FOLDER}/{file_path}.png")
os.makedirs(RESULT_FOLDER, exist_ok=True)

image.save(f"{RESULT_FOLDER}/{file_path}.png", "png")
