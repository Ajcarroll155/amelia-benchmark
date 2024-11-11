from langchain_core.language_models.llms import BaseLLM
from langchain_core.messages.base import BaseMessage
from typing_extensions import TypedDict, deprecated
from langgraph.graph import StateGraph, END
from langchain.retrievers import ContextualCompressionRetriever
from langchain_community.document_compressors.flashrank_rerank import FlashrankRerank
from agents.csv_agent import CSVAgent
from agents.rag_agent import RagAgent
from agents.response_agent import ResponseAgent
from agents.uprof_agent import UprofAgent
from agents.uprof_processor import process_uprof_csv
from langchain_community.embeddings import HuggingFaceInstructEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.embeddings import FastEmbedEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from flashrank import Ranker
from pathlib import Path

class AgentState(TypedDict):
    """
    The dictionary keeps track of the data required by the various nodes in the graph
    """

    question: str
    chat_history:list[BaseMessage]
    knowledge: str
    context: dict
    data_analysis: str
    generation: str

class Agent:
    """
    LangGraph agent integrates multiple agents into an LLM pipeline.
    """
    def __init__(self, llm: BaseLLM, file_path: str='', chat_history: list = []) -> None:
        """
        Initialize agent with llm, retriever, chat history and creates langgraph.

        Args:
            llm (_type_): llm model
            retriever (_type_): _description_
            chat_history (list, optional): _description_. Defaults to [].
        """
        # Set private fields
        self.llm = llm
        self.chat_history = chat_history
        self.file_path = file_path
        self.active_nodes = {}

        '''
        for file in self.files:
            metadata = file['file']['meta']
            if metadata['content_type'].split('/')[-1] == 'csv':
                if metadata['uprof_log'] == True:
                    self.uprof_logs.append(metadata['path'])
                else:
                    self.csv_files.append(metadata['path'])
        '''
        db_dir = "./knowledgebase/vectorstore"
        # Get retriever

        knowledge_base = Chroma(
            embedding_function=HuggingFaceInstructEmbeddings(model_name='hkunlp/instructor-xl'),
            persist_directory=db_dir,
            collection_metadata={"hnsw:space":"cosine"},
            collection_name="vectorstore")
        
        self.knowledge_retriever = self._init_retriever(knowledge_base.as_retriever(search_kwargs={"k": 10}))

        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1024, chunk_overlap=100
        )

        if file_path != '':
            self.embed_document(file_path)

        # List CSV agent in active nodes
        self.active_nodes["csv_node"] = CSVAgent._description()

        # Get RAG agent
        #self.rag_agent = RagAgent.get_agent(self.llm)
        self.active_nodes["rag_node"] = RagAgent._description()

        # Get final response generator
        self.final_response_generator = ResponseAgent.get_agent(self.llm)
        self.active_nodes["final_response"] = ResponseAgent._description()

        # Build state graph
        self.graph = StateGraph(AgentState)

        self.graph.add_node("rag_node", self.rag_node)
        self.graph.add_node("csv_node", self.csv_node)
        self.graph.add_node("uprof_node", self.uprof_node)
        self.graph.add_node("final_response", self.final_response)
        self.graph.add_node("knowledge_node", self.knowledge_node)
        

        # Set entry point
        self.graph.set_entry_point("knowledge_node")
        '''
        self.graph.add_conditional_edges("knowledge_node", self.has_upload)
        self.graph.add_conditional_edges("rag_node", self.has_tabular_data)
        self.graph.add_conditional_edges("csv_node", self.has_uprof)
        self.graph.add_edge("uprof_node", "final_response")
        self.graph.add_edge("final_response", END)
        '''
        self.graph.add_conditional_edges("knowledge_node", self.file_type)
        self.graph.add_edge("csv_node", "final_response")
        self.graph.add_edge("rag_node", "final_response")
        self.graph.add_edge("final_response", END)
        self.agent = self.graph.compile()

    def embed_document(self, file_path):
        self.file_ext = file_path.split('.')[-1]
        self.file_path = file_path
        if self.file_ext == 'pdf':
            print(Path.cwd())
            docs = PyPDFLoader(file_path=self.file_path).load()
            chunks = self.text_splitter.split_documents(docs)

            vector_store = Chroma.from_documents(
                documents=chunks,
                embedding=HuggingFaceInstructEmbeddings(model_name='hkunlp/instructor-xl')
            )
            self.retriever = vector_store.as_retriever(
                search_type = "similarity_score_threshold",
                search_kwargs={"k": 3, "score_threshold": 0.5, },
            )

    def file_type(self, state):
        """
        Selects agent based on input file extension
        """
        if self.file_ext == 'csv':
            return 'csv_node'
        else:
            return 'rag_node'

    def has_tabular_data(self, state):
        """
        Determines whether user has uploaded uprof log, regular csv, or nothing. 
        """
        if len(self.csv_files) > 0:
            return "csv_node"
        elif len(self.uprof_logs) > 0:
            return "uprof_node"
        return "final_response"

    def has_uprof(self, state):
        """
        Determines whether user has uploaded uprof log.
        """
        if len(self.uprof_logs) > 0:
            return "uprof_node"
        else:
            return "final_response"
    
    def has_upload(self, state):
        """
        Determines whether user has uploaded a file. 
        """
        if len(self.files) == 0:
            return 'final_response'
        else:
            return 'rag_node'

    def _init_retriever(self, retriever):
        """
        Initialize reranker.
        Using a BERT-based model to rerank retrieved document chunks,
        then returns top 3 relevant chunks. 

        Args:
            retriever (_type_): Retriever object

        Returns:
            _type_: Retriever with reranking added.
        """
        ranker = Ranker(model_name="ms-marco-MultiBERT-L-12", max_length=1024)
        compressor = FlashrankRerank(client=ranker, top_n = 3, model="ms-marco-MultiBERT-L-12")
        compression_retriever = ContextualCompressionRetriever(
            base_compressor=compressor, base_retriever=retriever
        )

        return compression_retriever


    def get_response(self, query, chat_history=[]):
        inputs = {"question": query, "chat_history": chat_history}
        self.chat_history = chat_history
        
        response = self.agent.invoke(inputs)
        #print("debug2", response)
        return response
    

    def chat_node(self, state):
        """
        Perform basic chat functionality

        Args:
            state (dict): The current graph state
        
        Returns:
            _type_: Append final result to generation
        """
        #print("---CHAT---")
        question = state['question']
        history = state['chat_history']

        response = self.chat_agent.invoke({"input":question, "chat_history":history})

        return {"generation": response}
    

    def csv_node(self, state):
        """
        Perform an agent-driven analysis of a csv file

        Args:
            state (dict): The current graph state
        
        Returns:
            _type_: Append final result to generation
        """
        question = state['question']
        history = state['chat_history']
        files = [self.file_path] if self.file_ext == 'csv' else []
        if len(files) > 0:
            agent = CSVAgent.get_agent(llm=self.llm, file_paths=files, chat_history=history)

            response = agent.invoke({"input":question, "chat_history":history})['output']
        else:
            response = "None"
        return {'data_analysis':response}
    
    
    def rag_node(self, state):
        """
        Answer questions based on retrieved context of an uploaded file

        Args:
            state (dict): The current graph state
        
        Returns:
            _type_: Append final result to generation
        """
        question = state['question']
        documents = self.retriever.get_relevant_documents(question)
        return {'context':documents}

    def knowledge_node(self, state):
        """
        Answer questions based on retrieved context of the knowledge base
        
        Args:
            state (dict): The current graph state
        
        Returns:
            _type_: Append final result to generation
        """
        question = state['question']

        documents = self.knowledge_retriever.get_relevant_documents(question)

        return {"knowledge": documents}


    def final_response(self, state):
        """
        Use all available information to generate a final response to the user's question
        Generates response based on knowledge, context, and data analysis results
        
        Args:
            state (dict): The current graph state
        
        Returns:
            _type_: Append final result to generation
        """
        question = state['question']
        history = state['chat_history']
        knowledge = state['knowledge']
        if 'context' in state.keys():
            context = state['context']
        else:
            context = 'None'
        if 'data_analysis' in state.keys():
            data_analysis = state['data_analysis']
        else:
            data_analysis = 'None'

        response = self.final_response_generator.invoke({
            'knowledge':knowledge,
            'context': context,
            'data_analysis': data_analysis,
            'chat_history': history,
            'input': question
        })

        return {'generation':response}
    
    def uprof_node(self, state):
        """
        Perform an agent-driven analysis of a AMDuProf log file
        
        Args:
            state (dict): The current graph state
        
        Returns:
            _type_: Append final result to data_analysis
        """
        log_path = self.uprof_logs[0]

        uprof_data = process_uprof_csv(log_path)
        agent = UprofAgent.get_agent(llm=self.llm, data=uprof_data)

        response = agent.invoke({'input':state['question']})['output']

        return {'data_analysis':response}



    @deprecated("Returns string of all active nodes")
    def get_active_nodes(self):
        """
        Gets a string of all active nodes

        Returns:
            _type_: _description_
        """
        nodes = self.active_nodes
        format_string = ""

        for node in nodes.keys():
            format_string = format_string + f"{node}: {nodes[node]}\n"
        
        return format_string
    
    @deprecated("Determine pipeline path after decision node")
    def agent_action(self, state):
        """
        Returns node after choosing action.

        Args:
            state (_type_): The current graph state

        Returns:
            _type_: 
        """
        print('---CHOOSING ACTION---')
        next_node = state['generation_agent']
        for node in self.active_nodes.keys():
            if node in next_node:
                return node

    @deprecated("Choose action")
    def choose_action(self, state):
        """
        Perform a query-based selection of agent used to generate response

        Args:
            state (dict): The current graph state
        
        Returns:
            _type_: Populate generation_agent field of state dictionary
        """
        print("---CHOOSE ACTION---")
        question = state['question']
        history = state['chat_history']
        active_nodes = self.get_active_nodes()

        file_names = []
        if len(self.files) > 0:
            for file in self.files:
                name = file.split('/')[-1]
                file_names.append(name)
        else:
            file_names.append('There are no files that can be used.')  
        decision = self.decision_agent.invoke({
            "input":question, "chat_history":history, "files":file_names, "active_nodes":active_nodes
            })

        return {"generation_agent":decision}
    

    @deprecated("Format document context")
    def _format_docs(self, docs: list):
        """
        Takes a list of Document objects, returns formatted list of 
        the source and content of each document.

        Args:
            docs (list): List of document objects retrieved from vector database

        Returns:
            _type_: string
        """
        formatted_docs = ["\n\n[source: {}, content: {}]".format(doc.metadata["source"], doc.page_content) for doc in docs]
        return "".join(formatted_docs)


