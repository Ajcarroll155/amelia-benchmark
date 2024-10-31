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
- **Python**: 3.9 - 3.12
- **GPU**: MI300 (gfx942)
- **ROCm**: 6.2
- **Docker**

## Installation and Setup

1. **Ensure the following are available in your development environment**:
   - Docker
   - Python 3.9 - 3.12
   - A Hugging Face account with an API token

2. **Clone the vllm repository**:
   ```bash
   git clone https://github.com/vllm-project/vllm.git
   ```

3. **Clone the Amelia Benchmark repository**:
   ```bash
   git clone https://github.com/Ajcarroll155/amelia-benchmark.git
   cd amelia-benchmark
   ```

4. **Install project requirements**:
   ```bash
   pip install -r requirements.txt
   ```

5. **Download necessary datasets**:
   
   Create dataset directory:
   ```bash
   mkdir datasets
   ```
   Download desired dataset into the datasets directory:
   - Upload-based Q&A: https://huggingface.co/datasets/glaiveai/RAG-v1/blob/main/glaive_rag_v1.json
    
7. **Run the vllm start script**:
   ```bash
   cd vllm-server
   bash start_vllm_server.sh
   ```

8. **To run the pipeline**:
   ```bash
   python main.py
   ```

## Datasets
