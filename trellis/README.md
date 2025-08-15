- Clone TRELLIS:
```bash
git clone --recurse-submodules https://github.com/microsoft/TRELLIS.git
```
- Copy setup_env.sh and main.py to TRELLIS repository
- Setup environment:
```bash
chmod +x setup_env.sh && \
./setup_env.sh
```
- Run:
```bash
conda activate trellis && \
export CUDA_HOME=$CONDA_PREFIX && \
export CC=$CONDA_PREFIX/bin/x86_64-conda-linux-gnu-cc && \
export CXX=$CONDA_PREFIX/bin/x86_64-conda-linux-gnu-c++ && \
export LD_LIBRARY_PATH=$CUDA_HOME/targets/x86_64-linux/lib:$LD_LIBRARY_PATH && \
export CPLUS_INCLUDE_PATH=$CUDA_HOME/targets/x86_64-linux/include:$CPLUS_INCLUDE_PATH
```
- Start server:
```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```
or
```bash
pm2 start trellis.config.js
```

- Test:
```bash
curl -X POST 87.197.140.238:40124/generate/ -F "prompt=A fantasy tree house" --output output.ply
```

- 3D View:

https://superspl.at/editor/

- One Click Setup:
```bash
curl -fsSL https://raw.githubusercontent.com/thong-pvn/scripts/main/trellis/one_click_setup.sh | bash
```
