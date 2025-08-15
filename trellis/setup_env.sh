#!/bin/bash

set -e

startTime=$(date +%s)

echo "[STEP 1/17][$(($(date +%s) - $startTime)) seconds] Loading environment variables"
CONDA_ENV_NAME=trellis
PM2_SERVER_HOST=0.0.0.0
PM2_SERVER_PORT=8000
echo "Env name: $CONDA_ENV_NAME"
echo "Host: $PM2_SERVER_HOST"
echo "Port: $PM2_SERVER_PORT"


echo "[STEP 2/17][$(($(date +%s) - $startTime)) seconds] Locating Conda base directory and initializing Conda..."
CONDA_BASE=$(conda info --base)
PATH="${CONDA_BASE}/bin/":$PATH
source "${CONDA_BASE}/etc/profile.d/conda.sh"


echo "[STEP 3/17][$(($(date +%s) - $startTime)) seconds] Checking for existing Conda environment..."
if conda env list | grep -q "$CONDA_ENV_NAME"; then
  echo "Removing existing Conda environment: $CONDA_ENV_NAME"
  conda env remove --name $CONDA_ENV_NAME --yes
else
  echo "No existing Conda environment found with name: $CONDA_ENV_NAME"
fi

# # Check this file in TRELLIS repository already, if not, echo error and exit
# if [ ! -f "setup.sh" ]; then
#   echo "TRELLIS repository is not found. Please clone it first and copy this file to TRELLIS repository before running this script.\n Run: git clone --recurse-submodules https://github.com/microsoft/TRELLIS.git"
#   exit 1
# fi

# Generate ${CONDA_ENV_NAME}_conda_env.yml file for setup environment
echo "[STEP 4/17][$(($(date +%s) - $startTime)) seconds] Generating ${CONDA_ENV_NAME}_conda_env.yml for Conda environment setup..."
if [ -f "${CONDA_ENV_NAME}_conda_env.yml" ]; then
  echo "File ${CONDA_ENV_NAME}_conda_env.yml already exists. It will be overwritten."
fi
rm -f ${CONDA_ENV_NAME}_conda_env.yml
cat <<EOF > ${CONDA_ENV_NAME}_conda_env.yml
name: $CONDA_ENV_NAME
channels:
  - defaults
  - conda-forge

dependencies:
  - python=3.11
  - pip
  - gxx_linux-64
  - gcc_linux-64
  - cuda-nvcc=12.1
  - cuda-toolkit=12.1
EOF

echo "[STEP 5/17][$(($(date +%s) - $startTime)) seconds] Creating and activating Conda environment..."
conda env create -f ${CONDA_ENV_NAME}_conda_env.yml
conda activate $CONDA_ENV_NAME
export PATH=/venv/$CONDA_ENV_NAME/bin:$PATH
conda info --env
echo $CONDA_ENV_NAME
echo $PATH
which python
python --version
export CUDA_HOME=$CONDA_PREFIX
export CC=$CONDA_PREFIX/bin/x86_64-conda-linux-gnu-cc
export CXX=$CONDA_PREFIX/bin/x86_64-conda-linux-gnu-c++
echo "CONDA_ENV_NAME = $CONDA_ENV_NAME, CUDA_HOME = $CUDA_HOME, CC = $CC, CXX = $CXX"

echo "[STEP 6/17][$(($(date +%s) - $startTime)) seconds] Installing torch"
pip uninstall torch torchvision torchaudio -y
# pip cache purge
pip install torch==2.4.0 torchvision==0.19.0 torchaudio==2.4.0 --index-url https://download.pytorch.org/whl/cu121
# 1. Check CUDA version (PyTorch runtime)
python -c "import torch; print('CUDA version (from PyTorch):', torch.version.cuda)"
# 2. Check PyTorch version
python -c "import torch; print('PyTorch version:', torch.__version__)"
# 3. Check C++11 ABI setting
python -c "import torch; print('C++11 ABI:', torch._C._GLIBCXX_USE_CXX11_ABI)"
# 4. Check Python version
python --version
# 5. Check platform and architecture
uname -s && uname -m
# 6. Enter https://github.com/Dao-AILab/flash-attention/releases, choose corresponding architecture release version
# FLASHATTN

echo "[STEP 7/17][$(($(date +%s) - $startTime)) seconds] Installing flash_attn"
pip install https://github.com/Dao-AILab/flash-attention/releases/download/v2.8.3/flash_attn-2.8.3+cu12torch2.4cxx11abiFALSE-cp311-cp311-linux_x86_64.whl
python -c "import flash_attn; print('flash-attn version:', flash_attn.__version__)"

# . ./setup.sh --basic --xformers --diffoctreerast --spconv --mipgaussian --kaolin --nvdiffrast
#--------------------------------------------------------------------------
# BASIC
rm -rf /tmp/extensions/*
echo "[STEP 8/17][$(($(date +%s) - $startTime)) seconds] Installing basic dependencies"
pip install pillow imageio imageio-ffmpeg tqdm easydict opencv-python-headless scipy ninja rembg onnxruntime trimesh open3d xatlas pyvista pymeshfix igraph transformers
pip install git+https://github.com/EasternJournalist/utils3d.git@9a4eb15e4021b67b12c460c7057d642626897ec8
# XFORMERS
echo "[STEP 9/17][$(($(date +%s) - $startTime)) seconds] Installing xformers"
pip install xformers==0.0.27.post2 --index-url https://download.pytorch.org/whl/cu121
# KAOLIN
echo "[STEP 10/17][$(($(date +%s) - $startTime)) seconds] Installing kaolin"
pip install kaolin -f https://nvidia-kaolin.s3.us-east-2.amazonaws.com/torch-2.4.0_cu121.html
# NVDIFFRAST
echo "[STEP 11/17][$(($(date +%s) - $startTime)) seconds] Installing nvdiffrast"
mkdir -p /tmp/extensions
git clone https://github.com/NVlabs/nvdiffrast.git /tmp/extensions/nvdiffrast
pip install /tmp/extensions/nvdiffrast
# DIFFOCTREERAST
echo "[STEP 12/17][$(($(date +%s) - $startTime)) seconds] Installing diffoctreerast"
# conda install -c conda-forge gxx_linux-64 gcc_linux-64
# export CC=$CONDA_PREFIX/bin/x86_64-conda-linux-gnu-cc
# export CXX=$CONDA_PREFIX/bin/x86_64-conda-linux-gnu-c++
# echo "CONDA_PREFIX = $CONDA_PREFIX"
# conda install nvidia::cuda-nvcc
mkdir -p /tmp/extensions
git clone --recurse-submodules https://github.com/JeffreyXiang/diffoctreerast.git /tmp/extensions/diffoctreerast
pip install /tmp/extensions/diffoctreerast
# MIPGAUSSIAN
echo "[STEP 13/17][$(($(date +%s) - $startTime)) seconds] Installing mip-splatting"
mkdir -p /tmp/extensions
git clone https://github.com/autonomousvision/mip-splatting.git /tmp/extensions/mip-splatting
pip install /tmp/extensions/mip-splatting/submodules/diff-gaussian-rasterization/
# SPCONV
echo "[STEP 14/17][$(($(date +%s) - $startTime)) seconds] Installing spconv"
pip install spconv-cu120
#--------------------------------------------------------------------------

echo "[STEP 15/17][$(($(date +%s) - $startTime)) seconds] Installing other dependencies"
pip install huggingface-hub fastapi uvicorn accelerate sentencepiece tokenizers diffusers bitsandbytes hatchling python-multipart


echo "[STEP 16/17][$(($(date +%s) - $startTime)) seconds] Generating PM2 config file..."
# Store the path of the Conda interpreter
CONDA_INTERPRETER_PATH=$(which python)
# Generate config.js file for PM2 with specified configurations
if [ -f "$CONDA_ENV_NAME.config.js" ]; then
  echo "File $CONDA_ENV_NAME.config.js already exists. It will be overwritten."
fi
rm -f $CONDA_ENV_NAME.config.js
cat <<EOF > $CONDA_ENV_NAME.config.js
module.exports = {
  apps: [{
    name: '${CONDA_ENV_NAME}_server',
    script: 'uvicorn',
    interpreter: '${CONDA_INTERPRETER_PATH}',
    args: 'main:app --host $PM2_SERVER_HOST --port $PM2_SERVER_PORT',
  }]
};
EOF

echo "[STEP 17/17][$(($(date +%s) - $startTime)) seconds] Checking torch version..."
python -c "import torch; print('torch version:', torch.__version__)"
python -c "import torchvision; print('torchvision version:', torchvision.__version__)"
python -c "import torchaudio; print('torchaudio version:', torchaudio.__version__)"
python -c "import torch; print('CUDA version:', torch.version.cuda); print('CUDA available:', torch.cuda.is_available())"
echo -e "\n\n[INFO][$(($(date +%s) - $startTime)) seconds] Ended ${CONDA_ENV_NAME}.config.js generated for PM2."
