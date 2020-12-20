# If using a colab runtime:

#!pip install pdfminer.six
#!pip install PyPDF2

# Imports
import io
import math
import re
import os
from tqdm import tqdm
from pdfminer.converter import TextConverter
from pdfminer.pdfinterp import PDFPageInterpreter
from pdfminer.pdfinterp import PDFResourceManager
from pdfminer.pdfpage import PDFPage
from PyPDF2 import PdfFileReader, PdfFileWriter

# Set file and directory paths
path = 'combined.pdf'
destination = 'temp/'

# Create text object for a given page in PDF
def pages(pdf_path):
    with open(pdf_path, 'rb') as fh:
        for page in tqdm(PDFPage.get_pages(fh, 
                                      caching=True,
                                      check_extractable=True)):
            resource_manager = PDFResourceManager()
            fake_file_handle = io.StringIO()
            converter = TextConverter(resource_manager, fake_file_handle)
            page_interpreter = PDFPageInterpreter(resource_manager, converter)
            page_interpreter.process_page(page)
            
            text = fake_file_handle.getvalue()
            yield text
    
            # close open handles
            converter.close()
            fake_file_handle.close()

# Iterate over pages in file and create individual files based off of student ID (regex)
def splitpdf(pdf_path,destination):
  
    pg_dict = {}
    pages_list = list(pages(pdf_path))
  
    for page in pages_list:
        vuid = re.search(r'(ID:)\s*[0-9]{8}',page)
        if vuid:
            page_id = vuid.group()[-8:]
            pg_dict.setdefault(page_id, []).append(pages_list.index(page))

    for ids,pgs in tqdm(pg_dict.items()):
        pdf = PdfFileReader(pdf_path)
        pdf_writer = PdfFileWriter()
        for p in pgs:
            current_page = pdf.getPage(p)
            pdf_writer.addPage(current_page)
        outputFilename = ids + '.pdf'
        pdfOutput = open(destination + outputFilename, 'wb')
        pdf_writer.write(pdfOutput)

        pdfOutput.close()

# Driver function
splitpdf(path,destination)