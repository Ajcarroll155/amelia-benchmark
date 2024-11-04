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
   RAG_URL=https://huggingface.co/datasets/glaiveai/RAG-v1/resolve/main/glaive_rag_v1.json
   ```

### Quick Start
**Run setup script**:
   In the amelia-benchmark directory:
   ```bash
   bash setup.sh
   ```
   The script will prompt you to include the rocmProfileData repository for tracing:
   ```bash
   Setup with tracing functionality (RPD)? [y/n]
   ```
   Input ```y``` to add RPD tracing to the project build, ```n``` to exclude.
   
   Running setup.sh accomplishes the following:
   - Install and set-up vLLM ROCm image
   - Install the rocmProfileData tracers (optional)
   - Creates virtual environment for development and installs dependencies
   - Downloads benchmarking datasets
   - Builds vllm-rocm-amelia container via docker compose
   - Opens vllm-rocm-amelia bash session in current terminal window

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
   This process will take some time.
5. **Create Python virtual environment**

   Navigate to the amelia-benchmark directory and create the python virtual environment:
   ```bash
   cd ../amelia-benchmark
   python -m venv benchmark_env
   ```
   Activate the environment:
   ```bash
   source ./benchmark_env/bin/activate
   ```
   Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
6. **Download Benchmarking Datasets**

   Create datasets directory:
   ```bash
   mkdir datasets
   cd datasets
   ```
   
   Download desired datasets:
   - RAG Q&A:
     Download the [GlaiveAI RAG Dataset](https://huggingface.co/datasets/glaiveai/RAG-v1/blob/main/glaive_rag_v1.json) and add it to ```amelia-benchmark/datasets```
     ```bash
     curl -o "./glaive_rag_v1.json" "$RAG_URL"
     ```
7. **Create Docker container**

   Navigate to the amelia-benchmark directory and build the container from docker-compose:
   ```bash
   docker compose up -d .
   ```
   If you are including RPD tracing, set the variable MOUNT_RPD=1 during execution:
   ```bash
   MOUNT_RPD=1 docker compose up -d .
   ```
   The docker compose command will automatically create the vllm-rocm-amelia container and start a vLLM server hosting the supplied model.

   To verify the container has been created and the necessary volumes mounted, start a bash session in the container and view the working directory:
   ```bash
   docker compose exec -it vllm-rocm-amelia sh -c "dir"
   ```
   If setup correctly, the working directory ```workspace``` should include the following:
   - ```amelia-benchmark/```
   - ```rocmProfileData/``` (If including tracing functionality)

9. **Setup tracing functionality (Optional)**

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

## Running the Pipeline

Before running the pipeline, make sure the virtual environment is active:
```bash
cd amelia-benchmark
source ./benchmark_env/bin/activate
```
Execution of the Amelia pipeline is handled in ```amelia-benchmark/main.py```.

Running the command ```python main.py``` will execute a basic pipeline test using the RAG dataset, uploading a document and responding to a query for *n* iterations.

On line **50** of ```main.py```, specify *n* to determine number of uploads/queries used in the test run.
```python
dataset = LoadGenerator.load_dataset(n)
```

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
