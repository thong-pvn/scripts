# main.py
from fastapi import FastAPI
from diffusers import BitsAndBytesConfig, SD3Transformer2DModel
from diffusers import StableDiffusion3Pipeline
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

def getSd35Pipe():
    pipe = StableDiffusion3Pipeline.from_pretrained("stabilityai/stable-diffusion-3.5-large", torch_dtype=torch.bfloat16)
    pipe = pipe.to("cuda")
    return pipe

def generateImage(prompt: str, pipeline: StableDiffusion3Pipeline):
    image = pipeline(
        width=512,
        height=1280,
        prompt=prompt+" fresh-color",
        num_inference_steps=80,
        negative_prompt="ugly, bad anatomy, blurry, pixelated obscure, unnatural colors, poor lighting, dull, and unclear, cropped, out of frame, missing body, lowres, low quality, artifacts, duplicate, morbid, mutilated, poorly drawn face, deformed, dehydrated, bad proportions",
        guidance_scale=7.5,
        max_sequence_length=512
    ).images[0]
    return image

def getTrellisPipeImage():
    pipeline = TrellisTextTo3DPipeline.from_pretrained("microsoft/TRELLIS-text-xlarge")
    pipeline.cuda()
    return pipeline

def getTrellisPipeText():
    pipeline = TrellisTextTo3DPipeline.from_pretrained("microsoft/TRELLIS-text-xlarge")
    pipeline.cuda()
    return pipeline

def generate3dObjectImage(image: Image, pipeline: TrellisImageTo3DPipeline):
    result = pipeline.run(
        image,
        seed=1,
        # Optional parameters
        sparse_structure_sampler_params={
            "steps": 100,
            "cfg_strength": 7.5,
        },
        slat_sampler_params={
            "steps": 50,
            "cfg_strength": 7.5,
        },
        formats=['gaussian']
    )
    return result

def generate3dObjectText(prompt: str, pipeline: TrellisTextTo3DPipeline):
    result = pipeline.run(
        prompt=prompt,                # Tham số bắt buộc: text prompt
        num_samples=1,                # Số lượng mẫu muốn tạo
        seed=42,                      # Random seed để tái tạo kết quả
        sparse_structure_sampler_params={
            "steps": 100,             # Số bước sampling cho sparse structure
            "cfg_strength": 7.5       # Độ mạnh của classifier-free guidance

        },
        slat_sampler_params={
            "steps": 50,              # Số bước sampling cho structured latent
            "cfg_strength": 7.5       # Độ mạnh của classifier-free guidance
        },
        formats=['gaussian']  # Các định dạng output
    )
    return result

app = FastAPI()

@app.on_event("startup")
async def startup_event():
    print("Starting up... initializing models...")
    app.state.sd35Pipe = getSd35Pipe()
    app.state.trellisPipeImage = getTrellisPipeImage()
    app.state.trellisPipeText = getTrellisPipeText()
    print("Models initialized!")

@app.post("/generate/")
async def generate(prompt: str = Form()) -> Response:
    t0 = time.time()
    print(f"[INFO] Generation starting for prompt: {prompt}")
    trellisPipeText = app.state.trellisPipeText
    outputs = generate3dObject(prompt, trellisPipeText)
    t1 = time.time()
    print(f"[INFO] Generation ended for prompt: {prompt}, took: {(t1 - t0) / 60.0} min")
    buffer = BytesIO()
    outputs['gaussian'][0].save_ply(buffer)
    buffer.seek(0)
    buffer = buffer.getbuffer()
    t2 = time.time()
    print(f"[INFO] Generation saving and encoding for prompt: {prompt}, took: {(t2 - t1) / 60.0} min")

    return Response(buffer, media_type="application/octet-stream")

@app.post("/generateimage/")
async def generate(prompt: str = Form()) -> Response:
    t0 = time.time()
    print(f"[INFO] Generation starting for prompt: {prompt}")
    sd35Pipe = app.state.sd35Pipe
    image = generateImage(prompt, sd35Pipe)
    trellisPipeImage = app.state.trellisPipeImage
    outputs = generate3dObject(image, trellisPipeImage)
    t1 = time.time()
    print(f"[INFO] Generation ended for prompt: {prompt}, took: {(t1 - t0) / 60.0} min")
    buffer = BytesIO()
    outputs['gaussian'][0].save_ply(buffer)
    buffer.seek(0)
    buffer = buffer.getbuffer()
    t2 = time.time()
    print(f"[INFO] Generation saving and encoding for prompt: {prompt}, took: {(t2 - t1) / 60.0} min")
    return Response(buffer, media_type="application/octet-stream")
