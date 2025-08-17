#!/bin/bash


echo "[STEP 1/11] Loading environment variables"
CONDA_ENV_NAME=trellis
PM2_SERVER_HOST=0.0.0.0
PM2_SERVER_PORT=8000


echo "[STEP 2/11] Environment variables loaded."
echo "Env name: $CONDA_ENV_NAME"
echo "Host: $PM2_SERVER_HOST"
echo "Port: $PM2_SERVER_PORT"

echo "[STEP 3/11] Setting script to exit on error..."
set -e


echo "[STEP 4/11] Locating Conda base directory and initializing Conda..."
CONDA_BASE=$(conda info --base)

if [ -z "${CONDA_BASE}" ]; then
  echo "Conda is not installed or not in the PATH"
  exit 1
fi

PATH="${CONDA_BASE}/bin/":$PATH
source "${CONDA_BASE}/etc/profile.d/conda.sh"


echo "[STEP 5/11] Checking for existing Conda environment..."
if conda env list | grep -q "$CONDA_ENV_NAME"; then
  echo "Removing existing Conda environment: $CONDA_ENV_NAME"
  conda env remove --name $CONDA_ENV_NAME
else
  echo "No existing Conda environment found with name: $CONDA_ENV_NAME"
fi

# Check this file in TRELLIS repository already, if not, echo error and exit
if [ ! -f "setup.sh" ]; then
  echo "TRELLIS repository is not found. Please clone it first and copy this file to TRELLIS repository before running this script.\n Run: git clone --recurse-submodules https://github.com/microsoft/TRELLIS.git"
  exit 1
fi


# Generate ${CONDA_ENV_NAME}_conda_env.yml file for setup environment
echo "[STEP 6/11] Generating ${CONDA_ENV_NAME}_conda_env.yml for Conda environment setup..."
if [ -f "${CONDA_ENV_NAME}_conda_env.yml" ]; then
  echo "File ${CONDA_ENV_NAME}_conda_env.yml already exists. It will be overwritten."
fi
rm -f ${CONDA_ENV_NAME}_conda_env.yml
cat <<EOF > ${CONDA_ENV_NAME}_conda_env.yml
name: $CONDA_ENV_NAME
channels:
  - defaults
  - conda-forge
  - nvidia
  - pytorch

dependencies:
  - python=3.10
  - pip
  - cuda-toolkit=11.8
  - cuda-nvcc=11.8
  - gcc=9
  - gxx=9
  - pytorch-cuda=11.8
  - pip:
      # Not use --index-url here, so run it in script
      # - torch==2.4.0
      # - torchvision==0.19.0
      # - torchaudio==2.4.0
      # - --index-url=https://download.pytorch.org/whl/cu118
      - huggingface-hub==0.34.4
      - fastapi==0.116.1
      - uvicorn==0.35.0
      - accelerate==1.10.0
      - sentencepiece==0.2.1
      - tokenizers==0.21.4
      - diffusers==0.34.0
      - bitsandbytes==0.47.0
      - hatchling==1.27.0
      - imageio==2.37.0
      - easydict==1.13
      - rembg==2.0.67
      - python-multipart==0.0.20
EOF


echo "[STEP 7/11] Creating and activating Conda environment..."
conda env create -f ${CONDA_ENV_NAME}_conda_env.yml
conda activate $CONDA_ENV_NAME
conda info --env

# CUDA_HOME=${CONDA_PREFIX}

# Store the path of the Conda interpreter
CONDA_INTERPRETER_PATH=$(which python)


# Install other dependencies
echo "[STEP 8/11] Installing torch"
pip uninstall torch torchvision torchaudio -y
pip cache purge
pip install torch==2.4.0 torchvision==0.19.0 torchaudio==2.4.0 --index-url https://download.pytorch.org/whl/cu118

# Install other dependencies
echo "[STEP 9/11] Installing other dependencies..."
start=$(date +%s)
# Replace
# PYTORCH_VERSION=$(python -c "import torch; print(torch.__version__)")
# into
# PYTORCH_VERSION=$(python -c "import torch; print(torch.__version__.split('+')[0].split('.post')[0]")
# in file setup.sh
# Add .split('+')[0].split('.post')[0] to get version without + and .post
sed -i 's|PYTORCH_VERSION=$(python -c "import torch; print(torch.__version__)")|PYTORCH_VERSION=$(python -c "import torch; print(torch.__version__.split(\x27+\x27)[0].split(\x27.post\x27)[0])")|' setup.sh
rm -rf /tmp/extensions/*

. ./setup.sh --basic --xformers --diffoctreerast --spconv --mipgaussian --kaolin --nvdiffrast
end=$(date +%s)
echo "[INFO] Other dependencies installed in $(($end - $start)) seconds"


# Generate config.js file for PM2 with specified configurations
echo "[STEP 10/11] Generating PM2 config file..."
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

echo "[STEP 11/11] Installing flash_attn"
python -c "import torch; print('torch version:', torch.__version__)"
python -c "import torchvision; print('torchvision version:', torchvision.__version__)"
python -c "import torchaudio; print('torchaudio version:', torchaudio.__version__)"
python -c "import torch; print('CUDA version:', torch.version.cuda); print('CUDA available:', torch.cuda.is_available())"

# get time
start=$(date +%s)
. ./setup.sh --flash-attn
end=$(date +%s)
echo "[INFO] Flash_attn installed in $(($end - $start)) seconds"

echo -e "\n\n[INFO] Ended ${CONDA_ENV_NAME}.config.js generated for PM2."
