from datetime import datetime
import requests
import os

def download_pdf_from_url(url, file_name):
    try:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        pdf_directory = os.path.abspath(os.path.join(current_dir, '..', '..', 'grobid_client_python', 'tests', 'test_pdf'))
        os.makedirs(pdf_directory, exist_ok=True)
        save_path = os.path.join(pdf_directory, file_name)

        # Send a GET request to the URL to retrieve the content
        response = requests.get(url, stream=True)
        response.raise_for_status()  # Raise an exception for bad status codes

        # Open a file in binary write mode to save the PDF content
        with open(save_path, 'wb') as pdf_file:
            # Iterate over the content in chunks and write to the file
            for chunk in response.iter_content(chunk_size=8192):
                pdf_file.write(chunk)

        print(f"PDF downloaded successfully and saved at: {save_path}")
        return True
    except Exception as e:
        print(f"Failed to download PDF: {e}")
        return False

url = 'https://drive.google.com/file/d/1MMPyrC79eFmplgabBhrqpNi6QSVOHD1p/view?usp=sharing'
file_name = 'article6.pdf'
download_pdf_from_url(url, file_name)