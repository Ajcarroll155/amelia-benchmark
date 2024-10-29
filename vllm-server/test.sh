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

VENV=".${PROJECT}-${DEVICE}-venv"
if [[ ! $VIRTUAL_ENV =~ $VENV ]] ; then
  . $VENV/bin/activate
fi
if [[ $VIRTUAL_ENV =~ $VENV ]] ; then
  echo "INFO: Successful environment - VIRTUAL_ENV=${VIRTUAL_ENV}" 
else
  echo "ERROR: Missing environment -> source setup.sh"
  exit
fi

[[ -z $(pip list | grep "vllm") ]] && echo "ERROR: vllm not installed properly" || echo "INFO: vllm installed" 

## Test
VLLM_STATUS=$(curl localhost:8000) 
# GOOD: {"detail":"Not Found"}
# ERROR: curl: (7) Failed to connect to localhost port 8000 after 0 ms: Connection refused
[[ $VLLM_STATUS =~ "Not Found" ]] && echo "INFO: vllm serve is running" || echo "ERROR: vllm serve is not running"

python vllm-client.py
