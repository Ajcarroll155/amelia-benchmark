from langchain_core.language_models.llms import BaseLLM
from langchain_core.runnables import Runnable
from langchain.prompts import BasePromptTemplate, PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from agents.pythontool import PythonAstREPLTool
from agents.uprof_processor import process_uprof_csv
from agents.create_react_agent import create_react_agent
from agents.format_instructions_prompt import FORMAT_INSTRUCTIONS, SUFFIX
from agents.agent import (
    AgentExecutor,
    BaseMultiActionAgent,
    BaseSingleActionAgent,
    RunnableAgent,
    RunnableMultiActionAgent
)
import pandas as pd
from typing import Union

class UprofAgent:

    @staticmethod
    def get_agent(llm:BaseLLM, data:dict) -> Runnable:
        report = data['report']
        cpu_top = data['cpu_topology']
        core_metrics = data['core_metrics']

        df_locals = {'cpu_top':cpu_top, 'core_metrics':core_metrics}
        tools = [PythonAstREPLTool(locals=df_locals)]

        top_head = str(cpu_top.head(2).to_markdown())
        metrics_head = str(core_metrics.head(2).to_markdown())
        prompt = UprofAgent.get_prompt()

        prompt_partial = prompt.partial(report=report)

        agent: Union[BaseSingleActionAgent, BaseMultiActionAgent] = RunnableAgent(
            runnable=create_react_agent(llm,tools,prompt_partial),
            input_keys_arg=["input"],
            return_keys_arg=["output"]
        )

        return AgentExecutor(
            agent=agent,
            tools=tools
        )

    @staticmethod
    def get_prompt() -> PromptTemplate:
        prefix = """You are an intelligent AI assistant specializing in computer processor profiling.
        You are working with an AMDuProf output log, which consists of a text summary and two pandas dataframes.
        The names of the dataframes are cpu_top and core_metrics. 
        cpu_top contains information about the CPU topology of the system in the report, and core_metrics contains the data collected during the profiling.
        Here is the text summary of the report:
        
        {report}
        
        You should use the tools below to answer the question posed of you:
        
        {tools}
        """
        template = '\n\n'.join([prefix, FORMAT_INSTRUCTIONS, SUFFIX])

        return PromptTemplate(template=template, input_variables=['report','tools','tool_names','input','agent_scratchpad'])



