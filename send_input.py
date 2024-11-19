import json
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import os

class LoadGenerator:

    def __init__(self):
        pass

    @staticmethod
    def load_dataset(useCase:str='PDF', numPoints:int=10):
        '''
        Get the selected number of items from the dataset.

        Args:
            numPoints(int, optional): The number of datapoints to collect. Defaults to 10

        Returns:
            List(Tuple): List of collected datapoints
        '''
        dataset_path = './datasets/'
        if useCase == 'PDF':
            dataset_path += 'glaive_rag_v1.json'
        elif useCase == 'CSV':
            dataset_path += 'csv_qa_dataset.json'

        with open(dataset_path, 'r') as dataset:
            data = json.load(dataset)
        
        if numPoints > len(data):
            numPoints = len(data)
        subset = data[:numPoints]

        if useCase == 'PDF':
            return LoadGenerator.load_pdf_dataset(numPoints=numPoints)
        elif useCase == 'CSV':
            print('The CSV dataset includes 4 potential queries for each file. How many would you like to include? (1-4)')
            numQueries = input()
            return LoadGenerator.load_csv_dataset(numPoints=numPoints,numQueries=numQueries)
        else:
            return None
    
    @staticmethod
    def load_pdf_dataset(numPoints:int=10):
        dpath = './datasets/glaive_rag_v1.json'

        with open(dpath, 'r') as dataset:
            data = json.load(dataset)
        
        if numPoints>len(data):
            numPoints = len(data)
        subset = data[:numPoints]

        formatted_subset = []
        for i in range(numPoints):
            entry = subset[i]
            docText = entry['documents']
            query = entry['question']
            path = LoadGenerator.create_pdf(
                content=docText,
                output_dir='./datasets/tempfiles',
                filename=f'document_{i}.pdf'
            )
            formatted_subset.append((path, query))
        
        return formatted_subset
    
    @staticmethod
    def load_csv_dataset(numPoints:int=10, numQueries:int=1):
        dpath = './datasets/csv_qa_dataset.json'

        with open(dpath, 'r') as dataset:
            data = json.load(dataset)
        
        if numPoints>len(data):
            numPoints = len(data)
        subset = data[:numPoints]

        formatted_subset = []
        for i in range(numPoints):
            entry = subset[i]
            fp = entry['path']
            q1 = entry['q_1']
            q2 = entry['q_2']
            q3 = entry['q_3']
            q4 = entry['q_4']
            if numQueries == 1:
                item = (fp, q1)
            if numQueries == 2:
                item = (fp, q1, q2)
            if numQueries == 3:
                item = (fp, q1, q2, q3)
            if numQueries == 4:
                item = (fp, q1, q2, q3, q4)
            formatted_subset.append(item)
        
        return formatted_subset


    @staticmethod
    def create_pdf(content: str, output_dir: str, filename: str = "output.pdf") -> str:
        '''
        Writes input text into a PDF document, stored in the specified output directory.

        Args:
            content(str): The text to write in the document
            output_dir(str): Path to location for the output file
            filename(str): Name of the output file. Deafults to output.pdf

        Returns:
            (str): The full path to the outputted PDF file
        '''
        # Ensure the output directory exists
        os.makedirs(output_dir, exist_ok=True)
        
        # Define the path for the output PDF file
        output_path = os.path.join(output_dir, filename)
        '''
        with open(output_path, 'w') as file:
            file.write(content)

        return output_path
        '''
        # Create a PDF with the specified content
        c = canvas.Canvas(output_path, pagesize=letter)
        text_object = c.beginText(40, 750)  # Starting position (x, y) on the page
        text_object.setFont("Helvetica", 12)

        # Split content into lines and add them to the PDF
        for line in content.splitlines():
            text_object.textLine(line)
        
        c.drawText(text_object)
        c.showPage()
        c.save()
        
        return output_path