import json
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import os

class LoadGenerator:

    def __init__(self):
        pass

    @staticmethod
    def load_dataset(numPoints:int=10):
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