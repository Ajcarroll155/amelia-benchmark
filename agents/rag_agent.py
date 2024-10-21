from langchain_core.language_models.llms import BaseLLM
from langchain_core.runnables import Runnable
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser

class RagAgent:
    
    @staticmethod
    def get_agent(llm:BaseLLM):
        template="""You are a highly intelligent AI assistant specializing in answering questions about AMD products.
        Use the following context to answer the user's questions:

        {context}

        Avoid telling the user that you used the context, just provide an in-depth answer to the question.
        You will be payed extra for each quality, in-depth response you produce.

        Here is the chat history: 

        {chat_history}

        User: {input}

        Assistant:
        """

        prompt = PromptTemplate(template=template, input_variables=['context','chat_history','input'])

        return prompt | llm | StrOutputParser()
    
    @staticmethod
    def _description():
        description = """
        A retrieval augmented generation (RAG) node. Uses context provided from a file/file(s) to answer the user's questions.
        This node should be used when the user has a question about the information contained within the text of a document.
        Do not use this node for data analysis, only questions that you think can be answered directly from a documents text.
        """

        return description
