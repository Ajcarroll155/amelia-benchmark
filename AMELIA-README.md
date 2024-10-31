<a id="readme-top"></a>
# Project Amelia

<!-- TABLE OF CONTENTS -->
<details>
  <summary>Table of Contents</summary>
  <ol>
    <li>
      <a href="#about-the-project">About The Project</a>
      <ul>
        <li><a href="#built-with">Built With</a></li>
      </ul>
    </li>
    <li>
      <a href="#getting-started">Getting Started</a>
      <ul>
        <li><a href="#prerequisites">Prerequisites</a></li>
        <li><a href="#installation">Installation</a></li>
      </ul>
    </li>
    <li><a href="#usage">Usage</a></li>
    <li><a href="#roadmap">Roadmap</a></li>
    <li><a href="#contributing">Contributing</a></li>
    <li><a href="#contact">Contact</a></li>
    <li><a href="#acknowledgments">Acknowledgments</a></li>
  </ol>
</details>



<!-- ABOUT THE PROJECT -->
## About The Project
Amelia is an interactive chatbot designed to answer any questions the user may have about the information in user-uploaded documents and the knowledge base of documentation ingested from the AMD website. The chatbot is also able to perform interactive data analysis on system log outputs from AMD system profiling software such as AMD uProf. The chatbot is powered by Llama3-70b. 


Features:
- PDF and CSV file upload capability
- Intuitive AI context retrieval from uploaded files via langgraph agents
- Interactive data analysis agents for tabular(CSV) data
- Designated AI agent for analyzing AMDuProf output logs
- Interactive AI chatbot with conversation memory
- Vector Database with 1000+ AMD technical documents
- Back-end webscraper for consistent database updates from AMD documentation hub

![PDF-AMELIA](assets/amelia_diagram.png)


<p align="right">(<a href="#readme-top">back to top</a>)</p>



### Built With


* [![OpenWebUI][OpenWebUI.com]][OpenWebUI-url]
* [![Pipelines][Pipelines.com]][Pipelines-url]
* [![LangChain][LangChain.com]][LangChain-url]
* [![LangGraph][LangGraph.com]][LangGraph-url]
* [![vLLM][VLLM.com]][VLLM-url]
* [![ngrok][ngrok.com]][ngrok-url]
* [![Chroma][Chroma.com]][Chroma-url]

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- GETTING STARTED -->
## Getting Started
Currently supports Linux. 
* ROCm 6.1
* MI210/MI300x

## Prerequisites
Make sure you have
* Docker
* Python 3.11
* Created a [LangSmith](https://smith.langchain.com) account and create a free API key
* Created a [Hugging Face](https://huggingface.co/) account and create a free API key
  
### Installation

1. Download docker image for vLLM for ROCm 6.1 environment.
```
docker pull sjchang220/vllm
```
2. Clone Project Amelia and navigate to the project directory
```
git clone https://github.com/cwortman-amd/profiling-agent.git
cd profiling-agent
```
3. Activate the vLLM Docker container
```
bash launch_vllm_rocm6.1.sh
```
4. Open a new terminal and run the `setup.sh` script. This installs the Python venv and Open WebUI and Pipelines dependencies.
```
bash setup.sh
```
5. Navigate to the Open WebUI `.env` file and add your Hugging Face and LangSmith API tokens.
```
vim Open-webui/.env
```
6. Open a new terminal and start the Open WebUI server. Use VS Code terminal to enable automatic port forwarding.
```
bash start_openwebui.sh
```
You can load the website at `http://localhost:8000`.
If you want to change the port that server uses, navigate to `profiling-agent/Open-webui/backend/start.sh` and change the port number on line 8.

7. Open a new terminal and start the pipelines server.
```
bash start_piplines.sh
```
Pipelines is running on port 9099, so make sure that Open WebUI has the port added as a connection by going to UI Settings > Admin Settings > Connections,
and under OpenAI API add the url `http://localhost:9099` and password `0p3n-w3bu!` if not already added. 

8. Create a new chat and under models select **Amelia**. Start asking questions!


<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- SOURCE CODE EXPLANATION -->
## Source Code
Functionality description of source code and alterations to Open-Webui.

### Open-Webui Alterations
Changes made to Open-Webui code to improve application functionality

#### open-webui/backend/main.py
  * `dispatch()`: Prevent deletion of chat_id from request body
  * `chat_completion_files_handler()`: Prevent deletion of files list from request body

#### open-webui/backend/config.py
  * Added `PIPELINES_DIR` constant for routing uploads to pipelines directory

#### open-webui/backend/apps/rag/main.py
  * `process_doc()`: Prevent embedding large CSV files in vector database

#### open-webui/backend/apps/webui/routers/files.py
  * `upload_file()`: Add document storage in pipelines directory
  * `upload_file()`: Add metadata flag for AMDuProf csv logs

### Amelia Pipeline Code
Location of source files for all pipeline functionalities

Directory: `open-webui/backend/pipelines/` 

#### AMD Documentation Vector Database
  * `knowledgebase/vectorstore`: Vector database persistent directory
  * `knowledgebase/webscraper.py`: Webscraper main file

#### Amelia Pipeline Framework
  * `pipelines/amelia_pipeline.py`: Custom pipeline execution file
  * `pipelines/files`: File storage for uploads

#### Langgraph Agents
  * `agents/langgraph_agent.py`: Langgraph initialization and execution file
  * `agents/csv_agent.py`: Class file for agent performing data analysis on CSV files
  * `agents/uprof_agent.py`: Class file for agent performing data analysis specifically on AMDuProf logs
  * `agents/response_agent.py`: Class file for agent generating final response from user input and all other context

#### Utility Files
  * `agents/create_pandas_dataframe_agent.py`: Source file for CSV agent creation function
  * `agents/create_react_agent.py`: Source file of basic ReAct agent for data analysis
  * `agents/pandas_agent_prompts.py`: Prompt constants for CSV/Pandas agent
  * `agents/format_instructions_prompt.py`: Output/Thought process formatting prompt for ReAct agents
  * `agents/react_parser.py`: Output parser for ReAct agents
  * `uprof_processor.py`: Parsing function to create context + dataframes from AMDuProf log outputs

  

## Profiling with Langsmith
The Amelia pipeline has integrated support for the Langsmith client, which can be used to to view pipeline execution sequentially and observe each individual action.

For more information about the Langsmith API, follow the link in the <a href="#acknowledgements">**Acknowledgements**</a> section of this file.
### Setup
* To utilize Langsmith profiling features, first create a .env file in your local copy of the repository.
* Then follow the [Langsmith Setup Tutorial](https://docs.smith.langchain.com/) to create the necessary environment variables
* The `Client()` object is already provided in the Amelia pipeline source file. Once setup is completed you will be able to profile pipeline calls on your langsmith account page.


<!-- USAGE EXAMPLES -->
## Usage

### Selecting the Amelia Pipeline on Open-Webui
On the Open-Webui interface, navigate to the 'Select Model' dropdown menu and select **Amelia**:
![SELECT-AMELIA](assets/Select_Amelia.png)
### Submitting a chat request
Once the model has been selected, type your request in the chat bar at the bottom of the screen, then press the arrow to send:
![SUBMIT-CHAT](assets/Submit_Amelia_Chat.png)
### Uploading Files
Select the '**+**' icon to the left of the chat bar, then select 'Upload Files'
![FILE-UPLOADS](assets/File_Uploads_Amelia.png)
### Running the webscraper to update knowledgebase
Execute the following linux process to run a sweep of the AMD documentation hub, downloading and embedding any newly added documents:
```sh
INSERT WEBSCRAPER COMMAND
```

_For more examples, please refer to the [Documentation](https://example.com)_

<p align="right">(<a href="#readme-top">back to top</a>)</p>



## Legacy User Interface: Streamlit Application
![Streamlit-UI](assets/Legacy_Streamlit_UI.png)
### Source
The `streamlit/` directory contains source code for an alternative front-end application leveraging streamlit. The main application file can be found in `streamlit/app.py`

### Execution
To run the Amelia pipeline with the streamlit user interface do the following:
  * Navigate to the streamlit directory:
    ```sh
    cd streamlit
    ```
  * Execute the app.py file using the streamlit library:
    ```sh
    streamlit run app.py
    ```



<!-- ROADMAP -->
## Roadmap

- [x] Basic RAG chatbot with streamlit UI on Mi210
- [x] Add tabular data agents (CSV)
- [x] Create webscraper for ingesting AMD documentation into vector database
- [x] Implement more robust user interface with Open-Webui
- [x] Implement pipelines framework and create langgraph project pipeline
- [x] Migrate servers and source code to Mi300x node
- [x] Integrate Open-Webui RAG system with langgraph pipeline
- [ ] Improve knowledgebase with more document metadata
- [ ] Add support for front-end features
  - [ ] Open-Webui citation display
  - [ ] Open-Webui chat title generation

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- CONTRIBUTING -->
## Contributing

Contributions are what make the open source community such an amazing place to learn, inspire, and create. Any contributions you make are **greatly appreciated**.

If you have a suggestion that would make this better, please fork the repo and create a pull request. You can also simply open an issue with the tag "enhancement".
Don't forget to give the project a star! Thanks again!

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

<p align="right">(<a href="#readme-top">back to top</a>)</p>




<!-- CONTACT -->
## Contact

Austin Carroll - [LinkedIn](https://www.linkedin.com/in/austin-carroll-a658b42a1/) - acarroll44@gatech.edu
Shen Zhang - [LinkedIn](https://www.linkedin.com/in/shenrun-zhang-772a2b183/) - sz81@rice.edu

Project Link: [Project Amelia](https://github.com/cwortman-amd/profiling-agent)

<p align="right">(<a href="#readme-top">back to top</a>)</p>


<!-- ACKNOWLEDGEMENTS -->
## Acknowledgements

Use this space to list resources you find helpful and would like to give credit to. I've included a few of my favorites to kick things off!

* [ReAct Style Prompting](https://www.promptingguide.ai/techniques/react)
* [Langsmith Developer Tool](https://www.langchain.com/langsmith)

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- MARKDOWN LINKS & IMAGES -->
<!-- https://www.markdownguide.org/basic-syntax/#reference-style-links -->
[contributors-shield]: https://img.shields.io/github/contributors/othneildrew/Best-README-Template.svg?style=for-the-badge
[contributors-url]: https://github.com/othneildrew/Best-README-Template/graphs/contributors
[forks-shield]: https://img.shields.io/github/forks/othneildrew/Best-README-Template.svg?style=for-the-badge
[forks-url]: https://github.com/othneildrew/Best-README-Template/network/members
[stars-shield]: https://img.shields.io/github/stars/othneildrew/Best-README-Template.svg?style=for-the-badge
[stars-url]: https://github.com/othneildrew/Best-README-Template/stargazers
[issues-shield]: https://img.shields.io/github/issues/othneildrew/Best-README-Template.svg?style=for-the-badge
[issues-url]: https://github.com/othneildrew/Best-README-Template/issues
[license-shield]: https://img.shields.io/github/license/othneildrew/Best-README-Template.svg?style=for-the-badge
[license-url]: https://github.com/othneildrew/Best-README-Template/blob/master/LICENSE.txt
[linkedin-shield]: https://img.shields.io/badge/-LinkedIn-black.svg?style=for-the-badge&logo=linkedin&colorB=555
[linkedin-url]: https://linkedin.com/in/othneildrew
[product-screenshot]: images/screenshot.png
[Next.js]: https://img.shields.io/badge/next.js-000000?style=for-the-badge&logo=nextdotjs&logoColor=white
[Next-url]: https://nextjs.org/
[React.js]: https://img.shields.io/badge/React-20232A?style=for-the-badge&logo=react&logoColor=61DAFB
[React-url]: https://reactjs.org/
[Vue.js]: https://img.shields.io/badge/Vue.js-35495E?style=for-the-badge&logo=vuedotjs&logoColor=4FC08D
[Vue-url]: https://vuejs.org/
[Angular.io]: https://img.shields.io/badge/Angular-DD0031?style=for-the-badge&logo=angular&logoColor=white
[Angular-url]: https://angular.io/
[Svelte.dev]: https://img.shields.io/badge/Svelte-4A4A55?style=for-the-badge&logo=svelte&logoColor=FF3E00
[Svelte-url]: https://svelte.dev/
[Laravel.com]: https://img.shields.io/badge/Laravel-FF2D20?style=for-the-badge&logo=laravel&logoColor=white
[Laravel-url]: https://laravel.com
[Bootstrap.com]: https://img.shields.io/badge/Bootstrap-563D7C?style=for-the-badge&logo=bootstrap&logoColor=white
[Bootstrap-url]: https://getbootstrap.com
[JQuery.com]: https://img.shields.io/badge/jQuery-0769AD?style=for-the-badge&logo=jquery&logoColor=white
[JQuery-url]: https://jquery.com 
[LangChain.com]: https://img.shields.io/badge/langchain-228B22?style=for-the-badge&logo=langchain&logoColor=white
[LangChain-url]: https://langchain.com
[LangGraph.com]: https://img.shields.io/badge/langgraph-228B22?style=for-the-badge&logo=langchain&logoColor=white
[LangGraph-url]: https://langchain.com/langgraph
[OpenWebUI.com]: https://img.shields.io/badge/open%20webui-A9A9A9?style=for-the-badge&logo=openwebui&logoColor=white
[OpenWebUI-url]: https://openwebui.com
[VLLM.com]: https://img.shields.io/badge/vllm-FFA500?style=for-the-badge&logo=vllm&logoColor=white
[VLLM-url]: https://docs.vllm.ai
[Pipelines.com]: https://img.shields.io/badge/pipelines-A9A9A9?style=for-the-badge&logo=pipelines&logoColor=white
[Pipelines-url]: https://github.com/open-webui/pipelines
[Chroma.com]: https://img.shields.io/badge/chroma-FFFF00?style=for-the-badge&logo=chroma&logoColor=white
[Chroma-url]: https://trychroma.com
[ngrok.com]: https://img.shields.io/badge/ngrok-000080?style=for-the-badge&logo=ngrok&logoColor=white
[ngrok-url]: https://ngrok.com
