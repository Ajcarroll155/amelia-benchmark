from agents.create_pandas_dataframe_agent import create_pandas_dataframe_agent
from langchain_core.language_models import BaseLLM
import agents.pandas_agent_prompts as prompts
import pandas as pd

class CSVAgent:

    @staticmethod
    def get_agent(llm:BaseLLM, file_paths:list[str] | str, chat_history=[]):
        
        dataframes = []
        for file in file_paths:
            df = pd.read_csv(file)
            dataframes.append(df)

        pandas_agent = create_pandas_dataframe_agent(llm, dataframes[0], verbose=False, allow_dangerous_code=True,
                                          agent_executor_kwargs={"handle_parsing_errors": True, "chat_history": chat_history},
                                          prefix=prompts.NEW_PREFIX,
                                          include_df_in_prompt=True,
                                          input_variables=["chat_history"])
        
        return pandas_agent
    
    @staticmethod
    def _description():
        description = """
        A CSV processing node. Creates dataframes from data in a CSV file and interacts with the dataframes to get the necessary information.
        This node should be used when the user has a question regarding a data in a CSV file.
        Only choose this node if the user is asking about a file with the .csv extension.
        """

        return description
