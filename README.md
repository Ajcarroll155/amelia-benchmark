# Amelia Benchmark

Benchmarking application utilizing project Amelia for the MLperf suite.

- **Model**: [Llama3 70B Instruct](https://huggingface.co/NousResearch/Meta-Llama-3-70B-Instruct)
- **LLM Serving Framework**: [vLLM](https://docs.vllm.ai/en/latest/)
- **Features**:
  - Knowledge-based Q&A
  - Upload-based Q&A
  - Tabular data analysis (CSV)
  
## RAG Pipeline
Amelia is an interactive chatbot designed to answer any questions the user may have about the information in user-uploaded documents and the knowledge base of documentation ingested from the AMD website. The chatbot is also able to perform interactive data analysis on system log outputs from AMD system profiling software such as AMD uProf. The chatbot is powered by Llama3-70b.

See [AMELIA-README.md](https://github.com/Ajcarroll155/amelia-benchmark/blob/main/AMELIA-README.md) for more information
## Requirements

- **OS**: Linux
- **Python**: 3.10
- **GPU**: MI300 (gfx942)
- **ROCm**: 6.2
- **Docker**

## Installation and Setup

**Ensure the following are available in your development environment:**
   - Docker
   - Python 3.10
   - A huggingface account with an API token

**Clone the project repository:**
   ```bash
   git clone https://github.com/Ajcarroll155/amelia-benchmark.git
   cd amelia-benchmark
   ```

**Setup environment:**
  
   Create a .env file from ```example.env``` and set the following variables:
   - ```CACHE_DIR```: path to model cache
   - ```MODEL```: model repository it is recommended to use the default NousResearch/Meta-Llama-3-70B-Instruct
   - ```API_KEY```: The API key associated with your OpenAI account
   
   Your final .env file should be similar to the following:
   ```bash
   CONTAINER_NAME=vllm-rocm-amelia
   CACHE_DIR=/path/to/your/model
   MODEL=NousResearch/Meta-Llama-3-70B-Instruct
   API_KEY=your-openai-api-key
   DATASET_DIR=./datasets
   RAG_URL=[link to rag dataset]
   ```

### Quick Start
**Setup Container**:

   In the amelia-benchmark directory:
   ```bash
   bash setup_container.sh
   ```
   The script will prompt you to include the rocmProfileData repository for tracing:
   ```bash
   Setup with tracing functionality (RPD)? [y/n]
   ```
   Input ```y``` to add RPD tracing to the project build, ```n``` to exclude.
   
   Running setup.sh accomplishes the following:
   - Install and set-up vLLM ROCm image
   - Download the rocmProfileData tracers (optional)
   - Downloads benchmarking datasets
   - Builds vllm-rocm-amelia container via docker compose
   - Opens vllm-rocm-amelia bash session in current terminal window

**Troubleshooting**:
   - RAG dataset download fails: If the RAG dataset JSON file contains only a URL, you can alternatively download the dataset from the link in step 6 of manual installation, and place it in the ```datasets``` directory
   - Bash session not opened after execution: To manually open a container bash session in the current terminal window, use the command:
     ```bash
     docker compose exec -it vllm-rocm-amelia bash
     ```

**Install Dependencies**

Once the container is running with a terminal window attached, run the ```install_env``` script:
```bash
bash install_env.sh
```
This script accomplishes the following:
- Installs APT dependencies for rocmProfileData
- Builds the RPD tracers
- Installs project dependencies for the Amelia pipeline

***Note***: Containers build with docker compose can be stopped in two different ways.
- ```docker compose down``` will completely dismantle the container removing installed dependencies. This will require the following commands to restart the container:
  ```bash
  docker compose up -d
  docker compose exec -it vllm-rocm-amelia bash
  bash install_env.sh
  ```
- ```docker compose stop vllm-rocm-amelia``` will only stop the container, and it can then be restarted using
  ```docker compose start vllm-rocm-amelia```

### Manual Installation
    
1. **Load environment variables**
   ```bash
   source .env
   ```
2. **Clone external repositories**

   Navigate to the parent directory of amelia-benchmark to add external dependencies
   - Clone vLLM
   ```bash
   git clone https://github.com/vllm-project/vllm.git
   ```
   - To include RPD tracing tools:
   ```bash
   cd amelia-benchmark
   git clone https://github.com/ROCm/rocmProfileData.git
   ```
4. **Build vLLM image**

   Navigate to the vllm directory to build vllm-rocm image:
   ```bash
   cd vllm
   ```
   Build the image with the following command:
   ```bash
   DOCKER_BUILDKIT=1 docker build -f Dockerfile.rocm --build-arg BASE_IMAGE="rocm/pytorch:rocm6.2.3_ubuntu22.04_py3.10_pytorch_release_2.3.0" -t vllm-rocm-amelia .
   ```
   This process will take some time, and can be skipped if the image 'vllm-rocm-amelia' is already present on the system.
   
5. **Download Benchmarking Datasets**
   
   Download desired datasets:
   - RAG Q&A:
     Download the [GlaiveAI RAG Dataset](https://huggingface.co/datasets/glaiveai/RAG-v1/blob/main/glaive_rag_v1.json) and add it to ```amelia-benchmark/datasets```
     ```bash
     curl -o "./glaive_rag_v1.json" "$RAG_URL"
     ```
6. **Create Docker container**

   Navigate to the amelia-benchmark directory and build the container from docker-compose:
   ```bash
   docker compose up -d
   ```
   The docker compose command will automatically create the vllm-rocm-amelia container and start a bash session in the current terminal window.

7. **Setup tracing functionality (Optional)**

   If the container was built including the rocmProfileData directory, the following steps will install the RPD tracing tools:
   - Update/Install apt packages
     ```bash
     apt update
     apt install sqlite3 libsqlite3-dev
     apt install libfmt-dev
     ```
   - Install RPD tracers:
     ```bash
     cd rocmProfileData
     make; make install
     ```
     
8. **Install pipeline dependencies**
   Navigate to the ```amelia-benchmark``` directory and run the following:
   ```bash
   pip install -r requirements.txt
   pip install langchain_community
   pip uninstall apex
   ```

## Running the Pipeline

Before running the pipeline, make sure the vLLM server is active:
```bash
python3 -m vllm.entrypoints.openai.api_server --model NousResearch/Meta-Llama-3-70B-Instruct --api-key token-abc123 --port 8000
```

Execution of the Amelia pipeline is handled in ```amelia-benchmark/main.py```.

Open a new terminal session inside the container:
```bash
docker exec -it vllm-rocm-amelia bash
```

```main.py``` requires two input arguments, ```USE_CASE``` and ```NUM_DATAPOINTS```:
```bash
python main.py [USE_CASE] [NUM_DATAPOINTS]
```
Use Cases:
- RAG Q&A via PDF upload: ```PDF```
- Data analysis Q&A via CSV upload: ```CSV```

### Tracing pipeline execution

If the rocmProfileData repository was included in the container setup, the RPD tracer can be used to collect performance data.

To run a pipeline test with RPD, execute ```run_rpd.sh``` in the amelia-benchmark directory:
```bash
cd amelia-benchmark
bash run_rpd.sh
```
This command will execute ```main.py``` through the RPD tracer and store the trace results in ```trace.rpd```.
To automatically copy the trace file in json format for readability, include the ```-json``` flag:
```bash
bash run_rpd.sh -json
```

## Datasets
