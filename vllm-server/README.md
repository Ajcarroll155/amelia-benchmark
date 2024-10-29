# VLLM Server

The vllm project allows to you independently verify the vLLM server function for checking Openai API.

## Prerequisites

- Python3.10 is required to build the vllm package properly
- ROCM VLLM docker container rocm-vllm:latest

## Getting Started

Execute the following in a bash terminal:

```bash
source setup.sh
./start.sh
./test.sh
```

## Debug

1. Docker fails to start: modify the docker run without -d, --detached for inspecting log messages. You will need to start ./test.sh in a second terminal.
2. Port 8000 is not reachable: check `docker ps -a` whether port is listed. Ensure 8000 is available, and if not find an available port.
3. Out of memory: verify that the GPU is available or use a smaller model.
4. cudaMemGetInfo(device) error: likely a corrupted ROCM driver. Reinstall ROCM and reboot.
5. Host with Python3.11 doesn't work but runs successfully with Python3.10. Docker container was Python3.9 so not related.
6. KeyEror: 'type' -> \_get_and_verify_max_len -> if rope_scaling is not None and rope_scaling["type"] != "su": New models such as Llama3.1-8B may not be fully supported.

## References

| Topic          | Link                                                                 |
| -------------- | -------------------------------------------------------------------- |
| Installation   | https://docs.vllm.ai/en/latest/getting_started/amd-installation.html |
| OpenAI Server  | https://docs.vllm.ai/en/latest/serving/openai_compatible_server.html |
| ROCM Container | https://github.com/rocm/vllm                                         |
