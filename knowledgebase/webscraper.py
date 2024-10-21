from selenium import webdriver
from selenium.webdriver.edge.service import Service as EdgeService
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.firefox.service import Service as FireFoxService
from selenium.webdriver.safari.service import Service as SafariService
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import requests
import os
import time
import geckodriver_autoinstaller
import csv
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceInstructEmbeddings
from langchain.text_splitter import CharacterTextSplitter
from PyPDF2 import PdfReader

# geckodriver_autoinstaller.install()

# AMD Documentation Hub URL
doc_hub = "https://www.amd.com/en/search/documentation/hub.html#sortCriteria=%40amd_release_date%20descending&numberOfResults=96"
# Path to WebDriver for Microsoft Edge
edge_driver_path = r".\edgedriver_win64\msedgedriver.exe"

# Keyword dictionary for filtering on the AMD Documentation Hub
keyword_dict = {
    'Form Factor':[
        'Servers',
        'Desktops',
        'Workstations',
        'Laptops',
        'Embedded Platforms',
        'SmartSwitch',
        'Semi-Custom'
    ],
    'Product Type':[
        'Processors',
        'Accelerators',
        'Graphics',
        'Networking Infrastructure',
        'Software & Applications',
        'Development Tools',
        'Adaptive SoCs & FPGAs',
    ],
    'Product Brand':[
        'EPYC',
        'EPYC Embedded',
        'Ryzen Threadripper PRO',
        'Ryzen Threadripper',
        'Ryzen PRO',
        'Ryzen',
        'Instinct',
        'Radeon RX',
        'Radeon HD',
        'Legacy Graphics',
        'Pensando',
        'Radeon R9|R7|R5',
        'Radeon 600|500|400',
        'Alveo',
        'Zynq Adaptive SoCs',
        'Vitis',
        'Versal Adaptive SoCs',
        'ROCm'
    ],
    'Document Type':[
        'Solution Briefs',
        'Performance Briefs',
        'White Papers',
        'Datasheets',
        'Design Tools',
        'Tuning Guides',
        'Programmer References',
        'Application Notes',
        'User Guides',
        'Product Briefs',
        'Other',
        'Infographics',
        'Reference Configurations',
        'Design Guides',
        'Specifications',
        'Revision Guides',
        'Customer Briefing Decks',
        'Instruction Set Architectures',
        'Errata',
        'Reference Architectures',
        'Software Optimization Guides',
        'eBooks',
        'Articles'
    ],
    'Applications & Technologies':[
        'High Performance Computing',
        'Database & Data Analytics',
        'Design & Simulation',
        'HCI & Virtualizaiton',
        'Cloud Computing',
        'Network & Infrastructure Acceleration',
        'AI & Machine Learning',
        'Hosting',
        'Financial Technologies',
        'Cloud Gaming',
        'Video Transcoding',
        'Compuational Storage',
        'Video AI Analytics',
        'Robotics',
        'Adaptive Computing',
        'Blockchain'
    ],
    'Industries':[
        'Data Center (Cloud & Hosting Services)',
        'Media & Entertainment',
        'Software & Sciences',
        'Design & Manufacturing',
        'Electronic Design Automation',
        'Healthcare & Sciences',
        'Supercomputing & Research',
        'Financial Services',
        'Oil & Gas (or Energy)',
        'Architecture, Engineering & Construction',
        'Retail & E-Commerce',
        'Telco & Networking',
        'Automotive',
        'Emulations & Prototyping',
        'Government',
        'Aerospace & Defense',
        'Broadcast & PRO AV',
        'Wired & Wireless Communications',
        'Test & Measurement',
        'Industrial & Vision',
        'Education',
        'Gaming',
        'Consumer Electronics'
    ],
    'Document Location':[
        'AMD.com',
        'Partner Hosted',
        'Parter Hosted;Partner Hosted'
    ],
    'Partner':[
        'HPE',
        'Dell',
        'Lenovo',
        'Microsoft Azure',
        'AWS',
        'Supermicro',
        'Cisco',
        'Google Cloud',
        'IBM Cloud',
        'Micron',
        'Samsung',
        'VMware',
        'ASUS'
    ],
    'Audience':[
        'Technical',
        'Business'
    ],
    'Archive Status':[
        'Active',
        'Archived'
    ]
}

# The main driver for navigating the doc hub
# 
# Uses selenium webdriver as a base
# Contains methods to abstract navigation process on AMD Documentation Hub only
class AMDDocumentationDriver:

    # The selenium webdriver used for navigation
    driver = None
    # Internal wait function for easy calls
    wait = None

    @staticmethod
    def read_downloaded_documents(record_file):
        if not os.path.exists(record_file):
            return set()
        
        with open(record_file, 'r', newline='', encoding='utf-8') as f:
            reader = csv.reader(f)
            downloaded_docs = {row[0] for row in reader}

        return downloaded_docs
    
    @staticmethod
    def scrape():
        download_record_file = "downloaded_files.csv"
        new_downloads = []
        downloaded_docs = AMDDocumentationDriver.read_downloaded_documents(download_record_file)

        driver = AMDDocumentationDriver(browser="firefox")
        
        cont = True
        while cont:
            print("hello world")
            links, names, dates = driver.get_docs_from_page()

            # Get only new links
            new_links = [link for link in links if link.split('/')[-1] not in downloaded_docs]

            print(new_links)

            if new_links:
                # # Only download new documents
                # AMDDocumentationDriver.download_files(new_links)

                with open(download_record_file, 'a', newline='',encoding='utf-8') as file:
                    writer = csv.writer(file)
                    for link, name, date in zip(links, names, dates):
                        sublink = link.split('/')[-1]
                        if sublink not in downloaded_docs:
                            writer.writerow([sublink, name, date, link])
                            new_downloads.append(os.path.join("./raw_files", sublink))

            if driver.has_next():
                driver.next_page()
            else:
                cont = False
        
        driver.exit_session()

        return new_downloads


    @staticmethod
    def vector_store_embedding(new_downloads):
        

        def get_pdf_chunks(raw_text):
            text_splitter = CharacterTextSplitter(
                separator="\n",
                chunk_size=500,
                chunk_overlap=100,
                length_function=len
            )
            chunks = text_splitter.split_text(raw_text)
            return chunks
        print("Saving to vector db")
        
        vector_store = Chroma(
            embedding_function=HuggingFaceInstructEmbeddings(model_name='hkunlp/instructor-xl'),
            persist_directory='./vector_store',
            collection_metadata={"hnsw:space":"cosine"})

        for pdf in new_downloads:
            reader = PdfReader(pdf)
            text = ""
            for page in reader.pages:
                text += page.extract_text()
            metadata = {
                "source": pdf[12:]
            }

            text_chunks = get_pdf_chunks(text)

            embedder = HuggingFaceInstructEmbeddings(model_name = 'hkunlp/instructor-xl')

            vector_store.add_texts(
                texts=text_chunks,
                metadatas=[metadata]*len(text_chunks)
                )
            


    # Downloads files present at given URL(s)
    # 
    # file_links(List[string]): URL addresses of desired files
    @staticmethod 
    def download_files(file_links):
        from pathlib import Path


        # Create the directory if it doesn't exist  
        if not os.path.exists('raw_files'):  
            os.makedirs('raw_files')  
        downloaded_files = []
        failed_downloads = []
        
        for link in file_links:
            
            try:
                
                # Get byte stream from url
                pdf_file = requests.get(url=link)
                pdf_file.raise_for_status()  # Raise an HTTPError for bad responses
                
                # Get file name from end of URL
                file_name = link.split('/')[-1]

                # Get current directory path
                script_dir = os.path.dirname(os.path.abspath(__file__))

                # Get path to directory containing downloaded pdf files
                raw_files_dir = os.path.join(script_dir, 'raw_files')  

                # Get path to pdf file
                file_path = os.path.join(raw_files_dir, file_name)
                # Create the pdf file directory if it doesn't exist  
                if not os.path.exists(raw_files_dir):  
                    os.makedirs(raw_files_dir)  

                # Write bytes to file
                file = Path(file_path)
                file.write_bytes(pdf_file.content)

                # Check that file is actually downloaded.
                tOut = 0
                while not os.path.exists(file_path) and tOut < 3:
                    time.sleep(1)
                    tOut += 1
                if tOut >= 3: 
                    print(f'File not Found at {link}')
                    failed_downloads.append(link)
                else:
                    print(f'Downloaded {file_name}')
                    downloaded_files.append(file_name)
            except Exception as e:
                print(f'Failed to download {link}.\n Exception: {e}')
        
        print(f'\nDOWNLOADS COMPLETE\nSuccessful Downloads: {len(downloaded_files)}\nUnsuccessful Downloads: {len(failed_downloads)}')


    # Initialize the driver
    #
    # browser(string): Lowercase representation of desired browser
    # driver_path(string): Path to driver executable for specified browser, default=None
    def __init__(self, browser, driver_path=None):

        # Setup selenium driver for browser
        if browser == 'edge':
            service = EdgeService(executable_path=driver_path)
            self.driver = webdriver.Edge(service=service)
        elif browser == 'chrome':
            service = ChromeService(executable_path=driver_path)
            self.driver = webdriver.Chrome(service=service)
        elif browser == 'firefox':
            #service = FireFoxService(executable_path=driver_path)
            ff_options = webdriver.FirefoxOptions()
            ff_options.add_argument('--headless')
            self.driver = webdriver.Firefox(options=ff_options)
        elif browser == 'safari':
            service = SafariService(executable_path=driver_path)
            self.driver = webdriver.Safari(service=service)
        
        self.driver.get(doc_hub)

        # Set wait function
        self.wait = WebDriverWait(self.driver, 20)


    # Waits for the presence of an element on the page
    # 
    # target(string): html tag of the element to wait for
    # input(string): html container element of the target
    # shadow_root(bool): Specifies whether the target is contained within a '#shadow_root' of the input
    def wait_for_element(self, target, input, shadow_root=False):
        
        # build Javascript for locating target element
        return_args = 'return arguments[0]'
        shadow_root_arg = '.shadowRoot'
        query_selector = f".querySelector('{target}') != null"
        if shadow_root:
            script = return_args+shadow_root_arg+query_selector
        else:
            script = return_args+query_selector

        # wait for element presence
        self.wait.until(
            lambda d: d.execute_script(script, input)
        )


    # Uses the pager to move to the next page of documentation
    def next_page(self):

        # Locate page body and the pager element within
        body = self.driver.find_element(By.TAG_NAME, 'body')
        self.wait_for_element('atomic-pager', body)
        atomic_pager = self.driver.execute_script('return arguments[0].querySelector("atomic-pager")', body)

        # Verify appearance of navigation button
        self.wait_for_element('[part="next-button"]', atomic_pager, shadow_root=True)

        # Access button html inside pager shadow root
        next_button = self.driver.execute_script('''
            let button = arguments[0].shadowRoot.querySelector('[part="next-button"]');
            return button
        ''', atomic_pager)

        # Click next button
        if next_button:
            clickable = self.wait.until(
                EC.element_to_be_clickable(next_button)
            )
            self.driver.execute_script('arguments[0].click();', clickable)

        # Small delay for page refresh
        time.sleep(1)
    

    # Checks if there is another page of documents
    #
    # Return(bool): Whether there is a next page
    def has_next(self):

        # Locate page body and pager element
        body = self.driver.find_element(By.TAG_NAME, 'body')
        self.wait_for_element('atomic-pager', body)
        atomic_pager = self.driver.execute_script('return arguments[0].querySelector("atomic-pager")', body)

        # Wait for next button
        self.wait_for_element('[part="next-button"]', atomic_pager, shadow_root=True)
        next_button = self.driver.execute_script('''
            let button = arguments[0].shadowRoot.querySelector('[part="next-button"]');
            return button
        ''', atomic_pager)

        # Check if next button is disabled
        if next_button:
            is_disabled = self.driver.execute_script('return arguments[0].hasAttribute("disabled")', next_button)
            return (is_disabled == False)
        else:
            return False


    # Extracts the URL address of all documents on a page
    #
    # Return(List[string]): List containing document URL addresses
    def get_docs_from_page(self):
        body = self.driver.find_element(By.TAG_NAME, 'body')

        # Locate document list within page body
        atomic_list = self.driver.execute_script('return arguments[0].querySelector("atomic-result-list")', body)
        self.wait_for_element('atomic-result',atomic_list, shadow_root=True)
        # Get individual result elements from list
        atomic_results = self.driver.execute_script('''
            shadow_root = arguments[0].shadowRoot;
            return shadow_root.querySelectorAll("atomic-result")
        ''', atomic_list)

        doc_links = []
        doc_names = []
        doc_dates = []
        # Iterate results and extract URLs
        for result in atomic_results:
            self.wait_for_element('a', result, shadow_root=True)

            resultLink = self.driver.execute_script('''
                let root = arguments[0].shadowRoot;
                let lTag = root.querySelector("a");
                return lTag                         
            ''', result)

            resultTitle = self.driver.execute_script('''
                let title = arguments[0].querySelector("atomic-result-text");
                return title
            ''', resultLink)

            resultDate = self.driver.execute_script('''
                let root = arguments[0].shadowRoot;
                let date = root.querySelector("atomic-result-date");
                return date
            ''', result)

            doc_links.append(resultLink.get_attribute("href"))
            doc_names.append(resultTitle.text)
            doc_dates.append(resultDate.text if resultDate is not None else 'No date')

        print(f'''
            Document: {doc_names[0]}
            Date Published: {doc_dates[0]}
            URL: {doc_links[0]}
        \n\n''')

        print(f'''
            Document: {doc_names[-1]}
            Date Published: {doc_dates[-1]}
            URL: {doc_links[-1]}
        \n\n''')

        return (doc_links, doc_names, doc_dates)


    # (IN PROGRESS) Applies filter settings to the displayed documents on a page
    #
    # keywords(List[string])
    def filter_by_keyword(self, keywords):
        keyword_targets = {}

        for kw in keywords:
            for key in keyword_dict.keys():
                if kw in keyword_dict[key]:
                    if key in keyword_targets.keys():
                        sublist = keyword_targets[key]
                    else:
                        sublist = []
                    sublist.append(kw)
                    keyword_targets.update({key:sublist})
        
        body = self.driver.find_element(By.TAG_NAME, 'body')

        for label in keyword_targets.keys():
            self.wait_for_element(label, body)
            atomic_facet = self.driver.execute_script(f'''
                return arguments[0].querySelector('[label="{label}"]')
            ''', body)
            for keyword in keyword_targets[label]:
                self.wait_for_element(f'[title="{keyword}"]', atomic_facet, shadow_root=True)
                checkBox = self.driver.execute_script(f'''
                    let span = arguments[0].querySelector('[title="{keyword}"]');
                    let label = span.parentNode;
                    let list_item = label.parentNode;
                    let button = list_item.getElementsByTagName('button');
                    return button
                ''', atomic_facet)
                if checkBox:
                    clickable = self.wait.until(
                        EC.element_to_be_clickable(checkBox)
                    )
                    self.driver.execute_script('arguments[0].click();', clickable)
                    time.sleep(1)


    # Ends the driver session
    def exit_session(self):
        self.driver.quit()

def main():

    new_downloads = AMDDocumentationDriver.scrape()
    # print(new_downloads)

    # AMDDocumentationDriver.vector_store_embedding(new_downloads)


    

    
    # driver = AMDDocumentationDriver(browser='firefox')

    # #driver.filter_by_keyword(['Tuning Guides'])
    # cont = True
    # while(cont):
    #     links,names,dates = driver.get_docs_from_page()
    #     if driver.has_next():
    #         driver.next_page()
    #     else:
    #         cont = False
    
    #     with open('document-metadata.txt', 'a') as file:
    #         for link, name, date in zip(links, names, dates):
    #             sublink = link.split('/')[-1]
    #             file.write(f"{sublink}, {name}, {date}, {link}\n")
        
    # driver.exit_session()

    

if __name__ == '__main__':
    main()


