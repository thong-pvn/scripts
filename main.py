# main.py
from fastapi import FastAPI
from huggingface_hub import login
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
from trellis.utils import render_utils, postprocessing_utils

# Go to: https://huggingface.co/settings/tokens
login(token="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")

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
    pipe = pipe.to("cuda")
    return pipe

    # For low memory usage case
    # model_id = "stabilityai/stable-diffusion-3.5-large"
    # nf4_config = BitsAndBytesConfig(
    #     load_in_4bit=True,
    #     bnb_4bit_quant_type="nf4",
    #     bnb_4bit_compute_dtype=torch.bfloat16
    # )
    # model_nf4 = SD3Transformer2DModel.from_pretrained(
    #     model_id,
    #     subfolder="transformer",
    #     quantization_config=nf4_config,
    #     torch_dtype=torch.bfloat16
    # )

    # pipeline = StableDiffusion3Pipeline.from_pretrained(
    #     model_id,
    #     transformer=model_nf4,
    #     torch_dtype=torch.bfloat16
    # )
    # pipeline.enable_model_cpu_offload()
    # return pipeline

def generateImage(prompt: str, pipeline: StableDiffusion3Pipeline):
    image = pipeline(
        prompt=prompt,
        num_inference_steps=40,
        guidance_scale=4.5,
        max_sequence_length=512,
    ).images[0]
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
        # Optional parameters
        # sparse_structure_sampler_params={
        #     "steps": 12,
        #     "cfg_strength": 7.5,
        # },
        # slat_sampler_params={
        #     "steps": 12,
        #     "cfg_strength": 3,
        # },
    )
    # outputs is a dictionary containing generated 3D assets in different formats:
    # - outputs['gaussian']: a list of 3D Gaussians
    # - outputs['radiance_field']: a list of radiance fields
    # - outputs['mesh']: a list of meshes
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
    # save_path = re.sub(r"\s+", "_", prompt.strip())
    print(f"[INFO] Generation starting for prompt: {prompt}")
    sd35Pipe = app.state.sd35Pipe
    image = generateImage(prompt, sd35Pipe)
    # image.save("whimsical.png")
    # # Load an image
    # image = Image.open("whimsical.png")
    trellisPipe = app.state.trellisPipe
    outputs = generate3dObject(image, trellisPipe)
    # # GLB files can be extracted from the outputs
    # glb = postprocessing_utils.to_glb(
    #     outputs['gaussian'][0],
    #     outputs['mesh'][0],
    #     # Optional parameters
    #     simplify=0.95,          # Ratio of triangles to remove in the simplification process
    #     texture_size=1024,      # Size of the texture used for the GLB
    # )
    # glb.export("sample.glb")
    # Save Gaussians as PLY files

    t1 = time.time()
    print(f"[INFO] Generation ended for prompt: {prompt}, took: {(t1 - t0) / 60.0} min")
    buffer = BytesIO()
    outputs['gaussian'][0].save_ply(buffer)
    buffer.seek(0)
    buffer = buffer.getbuffer()
    t2 = time.time()
    print(f"[INFO] Generation saving and encoding for prompt: {prompt}, took: {(t2 - t1) / 60.0} min")

    return Response(buffer, media_type="application/octet-stream")

