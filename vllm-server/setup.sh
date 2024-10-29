#!/bin/bash

PROJECT="vllm-server"

if [[ -z $DEVICE ]] ; then
  if [[ -n $(nvidia-smi --list-gpus | grep "ID:") ]] ; then
    # NVIDIA devices - cuda
    export DEVICE="cuda"
  elif [[ -n $(rocm-smi --showuniqueid | grep "ID:") ]] ;then
    # AMD devices - rocm
    export DEVICE="rocm"
  else
    # Default is CPU
    export DEVICE="cpu"
  fi
fi

echo "========================================"
echo "Setup: $PROJECT-$DEVICE"
echo "========================================"
echo "Setup Python Virtual Environment"
DEVICE=${DEVICE:-"cuda"}
VENV=".${PROJECT}-${DEVICE}-venv"
python -m venv $VENV; source $VENV/bin/activate
echo "VIRTUAL_ENV=${VIRTUAL_ENV}"

pip install --upgrade pip setuptools wheel
pip install --upgrade packaging numpy
pip install --upgrade ninja==1.10.2.4

export WORKDIR="$PWD"

echo "INFO: Install vLLM"
if [[ $DEVICE == "cuda" ]] ; then
  echo "INFO: NVIDIA-VLLM install --> pip install vllm"
  pip install vllm
elif [[ $DEVICE == "rocm" ]] ; then
  
  echo "INFO: ROCM-VLLM install --> git clone https://github.com/rocm/vllm"
  git clone https://github.com/rocm/vllm rocm-vllm
  cd rocm-vllm

  pip install --upgrade pip

  # Install PyTorch
  pip uninstall torch -y
  pip install --no-cache-dir --pre torch==2.6.0.dev20240918 --index-url https://download.pytorch.org/whl/nightly/rocm6.2

  # Build & install AMD SMI
  #pip install /opt/rocm/share/amd_smi

  # Install dependencies
  pip install --upgrade numba scipy huggingface-hub[cli]
  pip install "numpy<2"
  pip install -r requirements-rocm.txt
  pip install -U ninja==1.10.2.4

  echo "INFO: Triton install --> git clone https://github.com/OpenAI/triton.git"
  python3 -m pip install ninja cmake wheel pybind11
  pip uninstall -y triton
  git clone https://github.com/OpenAI/triton.git
  cd triton
  git checkout e192dba
  cd python
  pip3 install .
  cd ../..
  
  echo "INFO: Flash Attention install --> git clone https://github.com/ROCm/flash-attention.git"
  git clone https://github.com/ROCm/flash-attention.git
  cd flash-attention
  git checkout 3cea2fb
  git submodule update --init
  GPU_ARCHS="gfx90a" python3 setup.py install
  cd ..

  # Apply the patch to ROCM 6.1 (requires root permission)
  #wget -N https://github.com/ROCm/vllm/raw/fa78403/rocm_patch/libamdhip64.so.6 -P /opt/rocm/lib
  #rm -f "$(python3 -c 'import torch; print(torch.__path__[0])')"/lib/libamdhip64.so*

  # Build vLLM for MI210/MI250/MI300.
  export PYTORCH_ROCM_ARCH="gfx90a;gfx942"
  python3 setup.py develop
  cd $WORKDIR
else
  echo "ERROR: DEVICE=$DEVICE is not valid for this project"
fi

[[ -z $(pip list | grep "vllm") ]] && echo "ERROR: vllm not installed properly" || echo "INFO: vllm installed" 
pip check
