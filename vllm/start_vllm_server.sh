MODEL="NousResearch/Meta-Llama-3-70B-Instruct"
API_KEY="token-abc123"
CONTAINER_NAME="vllm-amelia"

DOCKER_BUILDKIT=1 docker build -f Dockerfile.rocm -t vllm-rocm .

docker run -it \
--network=host \
--group-add=video \
-p=8000:8000 \
--ipc=host \
--cap-add=SYS_PTRACE \
--security-opt seccomp=unconfined \
--device /dev/kfd \
--device /dev/dri \
-v /mnt/data-share/acaroll:/root/.cache \
-n vllm-amelia \
vllm-rocm \
python3 -m vllm.entrypoints.openai.api_server --model NousResearch/Meta-Llama-3-70B-Instruct --api-key token-abc123 --port 8000