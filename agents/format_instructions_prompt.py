# flake8: noqa
PREFIX = """Answer the following questions as best you can. You have access to the following tools:"""
FORMAT_INSTRUCTIONS = """Use the following format:

Question: the input question you must answer
Thought: you should always think about what to do. plan out each step of your process to help answer the question
Action: the action to take, should be one of {tool_names}. only include the tool name, nothing else.
Code Output: the python code that can be executed to help answer the question. this output should be valid python commands only. Please do not use import statements or try to plot anything. Make sure your code is enclosed in a print() statement so you can see the output.
Observation: the result of the action
... (this Thought/Action/Code Output/Observation can repeat N times)
Thought: I now know the final answer
Final Answer: the final answer to the original input question"""
SUFFIX = """Begin!

Question: {input}
Thought:{agent_scratchpad}"""
