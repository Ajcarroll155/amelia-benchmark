from langchain_community.llms.vllm import VLLMOpenAI
from agents.langgraph_agent import Agent
from langchain_core.language_models.llms import BaseLLM
from dotenv import load_dotenv
from pathlib import Path
from send_input import LoadGenerator

MODEL_REPO = "NousResearch/Meta-Llama-3-70B-Instruct"
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

def init_langgraph(file_path, llm) -> BaseLLM:
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


dataset = LoadGenerator.load_dataset()

'''
for item in dataset:
     print(f'Path: {item[0]}, Query: {item[1]}')
'''
llm = init_vllm()

i = 1
data_length = len(dataset)
for item in dataset:
    print(f'ITEM {i} OF {data_length}')
    file_path = item[0]
    query = item[1]

    agent = init_langgraph(llm=llm, file_path=file_path)
    response = agent.get_response(query)
    generation = response['generation']

    print(f'File Path: {file_path}\nQuestion: {query}\nAnswer: {generation}\n')
    i+=1
'''
print('-----PIPELINE TEST-----')
while (True):
    print('NEW QUERY\n')
    #file_path = input('Path to Input File:')
    file_path = '/home/acaroll/amelia-benchmark/input_dir/WWII_SHORT.pdf'
    #query = input('File Query:')
    query = 'When did the war begin?'

    llm = init_vllm()
    agent = init_langgraph(llm=llm, file_path=file_path)
    history = [f'User: {query}']

    response = agent.get_response(query, history)
    generation = response['generation']

    history.append(f'Assistant: {generation}')

    print(f'Response: {generation}\n\n')
    break
'''