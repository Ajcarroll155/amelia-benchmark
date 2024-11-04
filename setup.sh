#!/bin/bash

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
    cd ..
    # Clone rocmProfileData repository
    git clone https://github.com/ROCm/rocmProfileData.git
    cd amelia-benchmark
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
# Create dev environment
echo "
Creating virtual environment at amelia-benchmark/benchmark_env..."
python -m venv benchmark_env
source ./benchmark_env/bin/activate
echo "Installing requirements..."
pip install -r requirements.txt

# Set up Docker container
echo "
Creating project container..."
docker compose up -d .

# apt packages if using RPD
if [ "$use_tracing" = "y" ] || [ "$use_tracing" = "Y" ]; then
    echo "Installing dependencies for RPD..."
    docker compose exec vllm-rocm-amelia apt update
    docker compose exec vllm-rocm-amelia apt install sqlite3 libsqlite3-dev
    docker compose exec vllm-rocm-amelia apt install libfmt-dev
    docker compose exec vllm-rocm-amelia sh -c "cd rocmProfileData"
    echo "Installing tracers..."
    docker compose exec vllm-rocm-amelia sh -c "make && make install"
fi
echo "SETUP COMPLETE"
docker compose exec -it vllm-rocm-amelia sh -c "cd .."

exit 0