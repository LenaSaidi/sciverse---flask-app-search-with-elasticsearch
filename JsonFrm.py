from grobid_client_python.example import JsonGenr

def Json_ret(pdf_path):
    data = JsonGenr(pdf_path)
    return data

# if __name__ == "__main__":
#     path = r'C:\Users\Ross\Dropbox\PC\Downloads\tst2\sciverse---flask-app-search-with-elasticsearch\pdf_bib'
    
#     print(Json_ret(path))