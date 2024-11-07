#!/bin/bash
DATASET_DIR="./datasets"
RAG_URL="https://huggingface.co/datasets/glaiveai/RAG-v1/resolve/main/glaive_rag_v1.json"


source .env

# Check Python version
echo "Verifying python..."
PYTHON_VERSION=$(python3 --version 2>&1)
VERSION_MAJOR=$(echo "$PYTHON_VERSION" | awk '{print $2}' | cut -d'.' -f1)
VERSION_MINOR=$(echo "$PYTHON_VERSION" | awk '{print $2}' | cut -d'.' -f2)

# Check if the version is 3.10
if [ "$VERSION_MAJOR" -eq 3 ] && [ "$VERSION_MINOR" -eq 10 ]; then
    echo "Python verified ($PYTHON_VERSION)"
else
    echo "You are currently using $PYTHON_VERSION. To setup this project, please use Python 3.10."
    exit 1
fi

# Prompt for RPD tracing
echo "Setup with tracing functionality (RPD)? [y/n] "
read use_tracing
if [ "$use_tracing" = "y" ] || [ "$use_tracing" = "Y" ]; then
    export MOUNT_RPD=1
    echo "Cloning rocmProfileData..."
    # Clone rocmProfileData repository
    git clone https://github.com/ROCm/rocmProfileData.git
fi
cd ..

# Download vLLM
echo "
Setting up vLLM..."
git clone https://github.com/vllm-project/vllm
cd vllm

# Build vLLM ROCm image (This may take some time)
echo "
Building vLLM ROCm image..."
DOCKER_BUILDKIT=1 docker build -f Dockerfile.rocm --build-arg BASE_IMAGE="rocm/pytorch:rocm6.2.3_ubuntu22.04_py3.10_pytorch_release_2.3.0" -t vllm-rocm-amelia .
echo "DONE"

cd ..
cd amelia-benchmark

# Download datasets
mkdir datasets
echo "
Downloading RAG Q&A dataset..."
curl -o "$DATASET_DIR/glaive_rag_v1.json" "$RAG_URL"

# Set up Docker container
echo "
Creating project container..."
docker compose up -d 

exit 0