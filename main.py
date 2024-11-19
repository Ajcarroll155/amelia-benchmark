from langchain_community.llms.vllm import VLLMOpenAI
from agents.langgraph_agent import Agent
from langchain_core.language_models.llms import BaseLLM
from dotenv import load_dotenv
from pathlib import Path
from send_input import LoadGenerator
import sys

MODEL_REPO = "NousResearch/Meta-Llama-3-70B-Instruct"
ARG_ERROR_MSG = '''
ERROR: Invalid input arguments

Be sure to provide the desired use case AND number of datapoints in the function call.
USE CASES:
    PDF Q&A: PDF
    CSV Q&A: CSV
Use the following command:
python3 main.py [USE CASE] [NUMBER OF DATAPOINTS]
'''

load_dotenv()
def init_vllm(model=MODEL_REPO) -> BaseLLM:
    """
    Function initializes vLLM endpoint, serving as the base model for the langgraph agent.

    Args:
        model (_type_, optional): _description_. Defaults to MODEL_REPO.

    Returns:
        _type_: Langchain base llm object
    """
    llm = VLLMOpenAI(
    openai_api_key="token-abc123",
    openai_api_base="http://localhost:8000/v1",
    model_name=model,
    temperature=0,
    frequency_penalty=0.9,
    model_kwargs={}
    )
    return llm 

def init_langgraph(llm, file_path='') -> BaseLLM:
        """
        Function initializes langgraph agent. 

        Args:
            file_path (_str_): Path to input file
            llm (_BaseLLM_): LLM Endpoint

        Returns:
            Agent: Langgraph agent object
        """

        agent = Agent(
            llm=llm,
            file_path=file_path
        )

        return agent

def main():
    try:
        args = sys.argv()
        useCase = args[0]
        numPoints = args[1]
    except:
         print(ARG_ERROR_MSG)
         return
    
    print(f'Preparing Benchmark Dataset:\nUse Case: {useCase} | Datapoints: {numPoints}')
         
    dataset = LoadGenerator.load_dataset(useCase, numPoints)
    llm = init_vllm()
    agent = init_langgraph(llm=llm)
    i = 1
    data_length = len(dataset)
    for item in dataset:
        print(f'ITEM {i} OF {data_length}')

        file_path = item[0]
        print(f'File Path: {file_path}')
        agent.embed_document(file_path)

        t_output = f'File Path: {file_path}\n'
        queries = item[1:]
        for query in queries:
            response = agent.get_response(query)
            generation = response['generation']
            t_output += f'{query} ---> {generation}\n'
        print(t_output)
        i+=1

if __name__=='__main__':
     main()
