import json
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import os

class LoadGenerator:

    def __init__(self):
        pass

    @staticmethod
    def load_dataset(numPoints:int=10):
        '''
        Get the selected number of items from the dataset.

        Args:
            numPoints(int, optional): The number of datapoints to collect. Defaults to 10

        Returns:
            List(Tuple): List of collected datapoints
        '''
        with open('./datasets/glaive_rag_v1.json', 'r') as dataset:
            data = json.load(dataset)
        
        if numPoints > len(data):
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