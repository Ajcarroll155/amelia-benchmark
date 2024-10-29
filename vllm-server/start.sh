#!/bin/bash

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

MODEL="meta-llama/Meta-Llama-3.1-70B-Instruct"
API_KEY="token-abc123"
PORT=8000
CONTAINER_NAME="vllm"

## Start
# Reference: https://docs.vllm.ai/en/latest/serving/openai_compatible_server.html
echo "INFO: Start vllm openai compatible server"
echo "INFO: MODEL=$MODEL" 
echo "INFO: PORT=$PORT" 
if [[ "$DEVICE" == "cuda" ]] ; then
  VLLM_IMAGE="vllm/vllm:latest"
  GPU_ARGS="--runtime nvidia --gpus all --ipc=host"
  #docker run -d --rm $GPU_ARGS -v $HOME/.cache/huggingface:/root/.cache/huggingface -e "HUGGING_FACE_HUB_TOKEN=$HF_TOKEN" -p $PORT:8000 --name $CONTAINER_NAME $VLLM_IMAGE --model $MODEL 
  vllm serve $MODEL --dtype auto --api-key $API_KEY
  echo "INFO: VLLM_IMAGE=$VLLM_IMAGE - active"
elif [[ "$DEVICE" == "rocm" ]] ; then
  VLLM_IMAGE="rocm-vllm:latest"
  GPU_ARGS=" --network=host --device=/dev/kfd --device=/dev/dri --group-add=video --ipc=host --cap-add=SYS_PTRACE --security-opt seccomp=unconfined --privileged"
  #docker run -d --rm $GPU_ARGS -v $HOME/.cache/huggingface:/root/.cache/huggingface -e HF_TOKEN=$HF_TOKEN --name $CONTAINER_NAME $VLLM_IMAGE python3 -m vllm.entrypoints.openai.api_server --model $MODEL --api-key $API_KEY --port $PORT 
  MODEL=$MODEL VLLM_IMAGE=$VLLM_IMAGE VLLM_PORT=$PORT API_KEY=$API_KEY docker compose up -d
fi

echo "INFO: Wait 60s for server to accept connections" 
sleep 60 
VLLM_STATUS=$(curl localhost:$PORT) 
# GOOD: {"detail":"Not Found"}
# ERROR: curl: (7) Failed to connect to localhost port 8000 after 0 ms: Connection refused
#[[ $VLLM_STATUS =~ "Not Found" ]] && echo "INFO: vllm serve is running - $VLLM_IMAGE" || echo "ERROR: vllm serve is not running"
if [[ $VLLM_STATUS =~ "Not Found" ]]; then
  echo "INFO: vllm serve is running - $VLLM_IMAGE"
else
  echo "ERROR: vllm serve is not running. Connection refused."
  echo "INFO: Fetching Docker logs for details:"
  docker logs $CONTAINER_NAME  # Check container logs for more details
fi
