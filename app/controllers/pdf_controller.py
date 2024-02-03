# app/controllers/pdf_controller.py
import requests
import os

# def download_pdf_from_url(url, save_path):
#     try:
#         # Send a GET request to the URL to retrieve the content
#         response = requests.get(url, stream=True)
#         response.raise_for_status()  # Raise an exception for bad status codes

#         # Open a file in binary write mode to save the PDF content
#         with open(save_path, 'wb') as pdf_file:
#             # Iterate over the content in chunks and write to the file
#             for chunk in response.iter_content(chunk_size=8192):
#                 pdf_file.write(chunk)

#         print(f"PDF downloaded successfully and saved at: {save_path}")
#         return True
#     except Exception as e:
#         print(f"Failed to download PDF: {e}")
#         return False


def generate_unique_filename(prefix, extension):
    index = 1
    while True:
        filename = f"{prefix}{index}.{extension}"
        if not os.path.exists(os.path.join('tests', 'test_pdf', filename)):
            return filename
        index += 1

def download_pdf(pdf_url, pdf_path):
    # Send a GET request to the PDF URL
    response = requests.get(pdf_url)
    if response.status_code != 200:
        raise Exception(f"Failed to download PDF. HTTP status code: {response.status_code}")

    # Write the PDF content to a file
    with open(pdf_path, 'wb') as f:
        f.write(response.content)

# # Example usage:
# url = "https://drive.google.com/uc?export=download&id=1MMPyrC79eFmplgabBhrqpNi6QSVOHD1p"
# save_directory = r"\grobid_client_python\tests\test_pdf"
# file_name = "article.pdf"
# save_path = os.path.join(save_directory, file_name)
# print(save_path)

# # Download the PDF from the URL and save it locally
# download_pdf_from_url(url, save_path)



