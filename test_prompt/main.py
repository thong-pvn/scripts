# main.py
from fastapi import FastAPI
from diffusers import BitsAndBytesConfig, SD3Transformer2DModel
from diffusers import StableDiffusion3Pipeline
from diffusers import StableDiffusionPipeline
from diffusers import DDIMScheduler
from io import BytesIO
from fastapi import FastAPI, Form, Response
import time
import torch
import os
# os.environ['ATTN_BACKEND'] = 'xformers'   # Can be 'flash-attn' or 'xformers', default is 'flash-attn'
os.environ['SPCONV_ALGO'] = 'native'        # Can be 'native' or 'auto', default is 'auto'.
                                            # 'auto' is faster but will do benchmarking at the beginning.
                                            # Recommended to set to 'native' if run only once.

import imageio
from PIL import Image
from trellis.pipelines import TrellisImageTo3DPipeline
from trellis.pipelines import TrellisTextTo3DPipeline
from trellis.utils import render_utils, postprocessing_utils

os.environ["PYTORCH_CUDA_ALLOC_CONF"] = "expandable_segments:True"
if torch.cuda.is_available():
    print("[INFO] Clearing CUDA cache before model init...")
    torch.cuda.empty_cache()
    torch.cuda.ipc_collect()

# stabilityai/stable-diffusion-3.5-large
#----------------------------------------------------------------
# https://huggingface.co/stabilityai/stable-diffusion-3.5-large
def getSd35Pipe():
    pipe = StableDiffusion3Pipeline.from_pretrained("stabilityai/stable-diffusion-3.5-large", torch_dtype=torch.bfloat16)
    # pipe = StableDiffusionPipeline.from_pretrained(
    #         "stabilityai/stable-diffusion-2-1-base",
    #         torch_dtype=torch.bfloat16
    #     )
    
    pipe = pipe.to("cuda")
    return pipe

def generateImage(prompt: str, pipeline: StableDiffusion3Pipeline):
# def generateImage(prompt: str, pipeline: StableDiffusionPipeline):
    # Remove unwanted words from prompt
    unwanted_words = ["black", "brown", "gray", "dark"]
    cleaned_prompt = prompt
    for word in unwanted_words:
        cleaned_prompt = cleaned_prompt.replace(word, "").replace(word.capitalize(), "")
    
    generator = torch.Generator(device="cuda").manual_seed(42)
    image = pipeline(
        width=512,
        height=1280,
        generator=generator,
        # prompt=prompt,
        prompt=cleaned_prompt+ ", whole body, green background, top-down view, 45 degree tilt, camera angle from above",
        # prompt=prompt+ ", multmulti-view layout: front view, side view, back view, top view",
        # num_inference_steps=80,
        # num_images_per_prompt=1,
        negative_prompt="ugly, bad anatomy, blurry, pixelated obscure, unnatural colors, poor lighting, dull, and unclear, cropped, lowres, low quality, artifacts, duplicate, morbid, mutilated, poorly drawn face, deformed, dehydrated, bad proportions, shadow, lack of light, dark shadows, uneven lighting, harsh shadows, low light, poorly lit, overexposed, inconsistent illumination, one side dark, high contrast lighting, noisy background, black, brown",
        guidance_scale=7.5,
        max_sequence_length=512
    ).images[0]
    # Save generated image to specified directory with filename based on prompt
    output_dir = "/workspace/three-gen-subnet/batch_results"
    os.makedirs(output_dir, exist_ok=True)
    safe_prompt = "".join(c if c.isalnum() or c in ("-", "_") else "_" for c in prompt).strip("_")
    if not safe_prompt:
        safe_prompt = "output"
    image_path = os.path.join(output_dir, f"{safe_prompt}.png")
    image.save(image_path)
    return image

#----------------------------------------------------------------

# https://github.com/microsoft/TRELLIS/blob/main/example.py
#----------------------------------------------------------------

def getTrellisPipe():
    # Load a pipeline from a model folder or a Hugging Face model hub.
    pipeline = TrellisImageTo3DPipeline.from_pretrained("microsoft/TRELLIS-image-large")
    pipeline.cuda()
    return pipeline

def generate3dObject(image: Image, pipeline: TrellisImageTo3DPipeline):
    # Generate a 3D object from the 2D image using the TRELLIS pipeline.
    # Run the pipeline
    result = pipeline.run(
        image,
        seed=1,
        # sparse_structure_sampler_params={
        #     "steps": 100,
        #     "cfg_strength": 7.5
        # },
        # slat_sampler_params={
        #     "steps": 50,
        #     "cfg_strength": 7.5,
        # }
    )
    return result

#----------------------------------------------------------------
# Server

app = FastAPI()

# Init, load models
@app.on_event("startup")
async def startup_event():
    print("Starting up... initializing models...")
    app.state.sd35Pipe = getSd35Pipe()
    app.state.trellisPipe = getTrellisPipe()
    print("Models initialized!")

@app.post("/generate/")
async def generate(prompt: str = Form()) -> Response:
    t0 = time.time()
    print(f"[INFO] Generation starting for prompt: {prompt}")
    sd35Pipe = app.state.sd35Pipe
    image = generateImage(prompt, sd35Pipe)
    trellisPipe = app.state.trellisPipe
    outputs = generate3dObject(image, trellisPipe)
    t1 = time.time()
    print(f"[INFO] Generation ended for prompt: {prompt}, took: {(t1 - t0) / 60.0} min")
    buffer = BytesIO()
    outputs['gaussian'][0].save_ply(buffer)
    buffer.seek(0)
    buffer = buffer.getbuffer()
    t2 = time.time()
    print(f"[INFO] Generation saving and encoding for prompt: {prompt}, took: {(t2 - t1) / 60.0} min")

    return Response(buffer, media_type="application/octet-stream")
