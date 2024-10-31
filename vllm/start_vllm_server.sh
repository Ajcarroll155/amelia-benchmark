
MODEL="NousResearch/Meta-Llama-3-70B-Instruct"
API_KEY="token-abc123"
CONTAINER_NAME="vllm-amelia"

# Mounted Cache Directory: Replace with desired model cache location
CACHE_DIR="/mnt/data-share/acaroll" 

DOCKER_BUILDKIT=1 docker build -f Dockerfile.rocm -t vllm-rocm . # Build the latest vLLM ROCm image

# Run the vLLM container
docker run -it \
    --network=host \
    --group-add=video \
    -p 8000:8000 \
    --ipc=host \
    --cap-add=SYS_PTRACE \
    --security-opt seccomp=unconfined \
    --device /dev/kfd \
    --device /dev/dri \
    -v ${CACHE_DIR}:/root/.cache \
    -n $CONTAINER_NAME \
    vllm-rocm \
    python3 -m vllm.entrypoints.openai.api_server --model $MODEL --api-key $API_KEY --port 8000