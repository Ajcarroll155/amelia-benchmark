# flake8: noqa

PREFIX = """
You are working with a pandas dataframe in Python. The name of the dataframe is `df`.
You should use the tools below to answer the question posed of you:"""

NEW_PREFIX = """
You are working with a pandas dataframe in Python. The name of the dataframe is `df`.
When you generate code, make sure you use the print() function to display the output.
Below is the chat history between you and the user:
{chat_history}

You should use the tools below to answer the question posed of you:

"""

MULTI_DF_PREFIX = """
You are working with {num_dfs} pandas dataframes in Python named df1, df2, etc. You 
should use the tools below to answer the question posed of you:"""

SUFFIX_NO_DF = """
Begin!
Question: {input}
{agent_scratchpad}"""

SUFFIX_WITH_DF = """
This is the result of `print(df.head())`:
{df_head}

Begin!
Question: {input}
{agent_scratchpad}"""

SUFFIX_WITH_MULTI_DF = """
This is the result of `print(df.head())` for each dataframe:
{dfs_head}

Begin!
Question: {input}
{agent_scratchpad}"""

PREFIX_FUNCTIONS = """
You are working with a pandas dataframe in Python. The name of the dataframe is `df`."""

MULTI_DF_PREFIX_FUNCTIONS = """
You are working with {num_dfs} pandas dataframes in Python named df1, df2, etc."""

FUNCTIONS_WITH_DF = """
This is the result of `print(df.head())`:
{df_head}"""

FUNCTIONS_WITH_MULTI_DF = """
This is the result of `print(df.head())` for each dataframe:
{dfs_head}"""

FUNCTIONS_WITH_DF_LARGE = """
This is the result of `print(df.columns)`:
{df_cols}"""

FUNCTIONS_WITH_MULTI_DF_LARGE = """
This is the result of `print(df.columns)` for each dataframe:
{df_cols}"""

SUFFIX_WITH_DF_LARGE = """
This is the result of `print(df.columns)`:
{df_cols}

Begin!
Question: {input}
{agent_scratchpad}"""

SUFFIX_WITH_MULTI_DF_LARGE = """
This is the result of `print(df.columns)` for each dataframe:
{df_cols}

Begin!
Question: {input}
{agent_scratchpad}"""