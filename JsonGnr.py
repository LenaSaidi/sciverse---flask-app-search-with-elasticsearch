from grobid_client.grobid_client import GrobidClient
import xml.etree.ElementTree as ET
import json
import os



def JsonGenr(pdf_path,article_name):


    client = GrobidClient(config_path="./grobid_client_python/config.json")
    client.process("processFulltextDocument", pdf_path, output="./tests/test_out/", consolidate_citations=False, tei_coordinates=True, force=False)
    def parse_xml(xml_path):
        tree = ET.parse(xml_path)
        root = tree.getroot()
        return root

    def extract_authors(element):
        authors = []
        for author_element in element.findall('.//tei:author', namespaces={'tei': 'http://www.tei-c.org/ns/1.0'}):
            name = author_element.findtext('tei:persName/tei:surname', '', namespaces={'tei': 'http://www.tei-c.org/ns/1.0'})
            email = author_element.findtext('tei:email', '', namespaces={'tei': 'http://www.tei-c.org/ns/1.0'})

            # Only include authors with both name and email
            if name and email:
                author_data = {
                    'name': name,
                    'email': email,
                    'institutions': []
                }

                for aff_element in author_element.findall('.//tei:affiliation', namespaces={'tei': 'http://www.tei-c.org/ns/1.0'}):
                    institution_name = aff_element.findtext('tei:orgName[@type="department"]', '', namespaces={'tei': 'http://www.tei-c.org/ns/1.0'})
                    author_data['institutions'].append({'institution_name': institution_name})

                authors.append(author_data)

        return authors

    def extract_keywords(element):
        return [term.text for term in element.findall('.//tei:term', namespaces={'tei': 'http://www.tei-c.org/ns/1.0'})]

    def extract_references(element):
        return [ref.text for ref in element.findall('.//tei:listBibl/tei:biblStruct/tei:analytic/tei:title', namespaces={'tei': 'http://www.tei-c.org/ns/1.0'})]

    def extract_full_text(element):
        return ' '.join(paragraph.text for paragraph in element.findall('.//tei:body/tei:div/tei:p', namespaces={'tei': 'http://www.tei-c.org/ns/1.0'}))

    def extract_abstract(element):
        return ' '.join(paragraph.text for paragraph in element.findall('.//tei:abstract/tei:div/tei:p', namespaces={'tei': 'http://www.tei-c.org/ns/1.0'}))

    def parse_xml_to_json(xml_path, json_path):
        root = parse_xml(xml_path)

        data = {
            'title': root.findtext('.//tei:titleStmt/tei:title[@type="main"]', '', namespaces={'tei': 'http://www.tei-c.org/ns/1.0'}),
            'abstract': extract_abstract(root),
            'authors': extract_authors(root),
            'keywords': extract_keywords(root),
            'references': extract_references(root),
            'full_text': extract_full_text(root),
        }

        with open(json_path, 'w') as json_file:
            json.dump(data, json_file, indent=2)
            return data
#______________ CHOFI HKD T'UTILISIHA ________________________
    # # Example usage:
    # xml_path = "./tests/test_out/test.grobid.tei.xml"
    # json_path = "./tests/test_out/Jsonfile.json"
    # print(parse_xml_to_json(xml_path, json_path))
    # return parse_xml_to_json(xml_path, json_path)

    # Example usage:
        

    xml_filename = f"{article_name}.grobid.tei.xml"
    xml_path = os.path.join("./tests/test_out", xml_filename)

    # xml_path = "./tests/test_out/article9.grobid.tei.xml"

    json_path = "./tests/test_out/Jsonfile.json"
    json_data = parse_xml_to_json(xml_path, json_path)


    # Remove the XML file
    # os.remove(xml_path)
    # os.remove(json_path)

    return json_data




# def JsonGenr(pdf_path):
#     client = GrobidClient(config_path="./grobid_client_python/config.json")
#     client.process("processFulltextDocument", pdf_path, output="./tests/test_out/", consolidate_citations=False, tei_coordinates=True, force=False)
#     def parse_xml(xml_path):
#         tree = ET.parse(xml_path)
#         root = tree.getroot()
#         return root

#     def extract_authors(element):
#         authors = []
#         for author_element in element.findall('.//tei:author', namespaces={'tei': 'http://www.tei-c.org/ns/1.0'}):
#             name = author_element.findtext('tei:persName/tei:surname', '', namespaces={'tei': 'http://www.tei-c.org/ns/1.0'})
#             email = author_element.findtext('tei:email', '', namespaces={'tei': 'http://www.tei-c.org/ns/1.0'})

#             # Only include authors with both name and email
#             if name and email:
#                 author_data = {
#                     'name': name,
#                     'email': email,
#                     'institutions': []
#                 }

#                 for aff_element in author_element.findall('.//tei:affiliation', namespaces={'tei': 'http://www.tei-c.org/ns/1.0'}):
#                     institution_name = aff_element.findtext('tei:orgName[@type="department"]', '', namespaces={'tei': 'http://www.tei-c.org/ns/1.0'})
#                     author_data['institutions'].append({'institution_name': institution_name})

#                 authors.append(author_data)

#         return authors

#     def extract_keywords(element):
#         return [term.text for term in element.findall('.//tei:term', namespaces={'tei': 'http://www.tei-c.org/ns/1.0'})]

#     def extract_references(element):
#         return [ref.text for ref in element.findall('.//tei:listBibl/tei:biblStruct/tei:analytic/tei:title', namespaces={'tei': 'http://www.tei-c.org/ns/1.0'})]

#     def extract_full_text(element):
#         return ' '.join(paragraph.text for paragraph in element.findall('.//tei:body/tei:div/tei:p', namespaces={'tei': 'http://www.tei-c.org/ns/1.0'}))

#     def extract_abstract(element):
#         return ' '.join(paragraph.text for paragraph in element.findall('.//tei:abstract/tei:div/tei:p', namespaces={'tei': 'http://www.tei-c.org/ns/1.0'}))

#     def parse_xml_to_json(xml_path, json_path):
#         root = parse_xml(xml_path)

#         data = {
#             'title': root.findtext('.//tei:titleStmt/tei:title[@type="main"]', '', namespaces={'tei': 'http://www.tei-c.org/ns/1.0'}),
#             'abstract': extract_abstract(root),
#             'authors': extract_authors(root),
#             'keywords': extract_keywords(root),
#             'references': extract_references(root),
#             'full_text': extract_full_text(root),
#         }

#         with open(json_path, 'w') as json_file:
#             json.dump(data, json_file, indent=2)
#             return data
# #______________ CHOFI HKD T'UTILISIHA ________________________
#     # # Example usage:
#     # xml_path = "./tests/test_out/test.grobid.tei.xml"
#     # json_path = "./tests/test_out/Jsonfile.json"
#     # print(parse_xml_to_json(xml_path, json_path))
#     # return parse_xml_to_json(xml_path, json_path)

#     # Example usage:
#     xml_path = "./tests/test_out/article8.grobid.tei.xml"
#     json_path = "./tests/test_out/Jsonfile.json"
#     json_data = parse_xml_to_json(xml_path, json_path)


#     # Remove the XML file
#     os.remove(xml_path)
#     os.remove(json_path)

#     return json_data


    # # Parse XML to JSON
    # json_data = parse_xml_to_json(xml_path)

    # # Remove the XML file
    # os.remove(xml_path)

    # return json_data



# def JsonGenr(pdf_path):
#     # Define the output directory path
#     path = os.path.dirname(pdf_path)

#     # Ensure the output directory exists
#     os.makedirs(path, exist_ok=True)

#     # Initialize GROBID client
#     client = GrobidClient(config_path="./grobid_client_python/config.json")

#     # Process the PDF file with GROBID
#     client.process("processFulltextDocument", path, output="./tests/test_out/", consolidate_citations=False, tei_coordinates=True, force=False)

#     # Function to parse XML content
#     def parse_xml(xml_path):
#         tree = ET.parse(xml_path)
#         root = tree.getroot()
#         return root

#     # Function to extract authors from XML
#     def extract_authors(element):
#         authors = []
#         for author_element in element.findall('.//tei:author', namespaces={'tei': 'http://www.tei-c.org/ns/1.0'}):
#             name = author_element.findtext('tei:persName/tei:surname', '', namespaces={'tei': 'http://www.tei-c.org/ns/1.0'})
#             email = author_element.findtext('tei:email', '', namespaces={'tei': 'http://www.tei-c.org/ns/1.0'})

#             # Only include authors with both name and email
#             if name and email:
#                 author_data = {
#                     'name': name,
#                     'email': email,
#                     'institutions': []
#                 }

#                 for aff_element in author_element.findall('.//tei:affiliation', namespaces={'tei': 'http://www.tei-c.org/ns/1.0'}):
#                     institution_name = aff_element.findtext('tei:orgName[@type="department"]', '', namespaces={'tei': 'http://www.tei-c.org/ns/1.0'})
#                     author_data['institutions'].append({'institution_name': institution_name})

#                 authors.append(author_data)

#         return authors

#     # Function to extract keywords from XML
#     def extract_keywords(element):
#         return [term.text for term in element.findall('.//tei:term', namespaces={'tei': 'http://www.tei-c.org/ns/1.0'})]

#     # Function to extract references from XML
#     def extract_references(element):
#         return [ref.text for ref in element.findall('.//tei:listBibl/tei:biblStruct/tei:analytic/tei:title', namespaces={'tei': 'http://www.tei-c.org/ns/1.0'})]

#     # Function to extract full text from XML
#     def extract_full_text(element):
#         return ' '.join(paragraph.text for paragraph in element.findall('.//tei:body/tei:div/tei:p', namespaces={'tei': 'http://www.tei-c.org/ns/1.0'}))

#     # Function to extract abstract from XML
#     def extract_abstract(element):
#         return ' '.join(paragraph.text for paragraph in element.findall('.//tei:abstract/tei:div/tei:p', namespaces={'tei': 'http://www.tei-c.org/ns/1.0'}))

#     # Function to parse XML to JSON
#     def parse_xml_to_json(xml_path):
#         root = parse_xml(xml_path)

#         data = {
#             'title': root.findtext('.//tei:titleStmt/tei:title[@type="main"]', '', namespaces={'tei': 'http://www.tei-c.org/ns/1.0'}),
#             'abstract': extract_abstract(root),
#             'authors': extract_authors(root),
#             'keywords': extract_keywords(root),
#             'references': extract_references(root),
#             'full_text': extract_full_text(root),
#         }

#         return data

#     # Construct the XML file path
#     xml_path = os.path.join(output_dir, "test.grobid.tei.xml")

#     # Parse XML to JSON
#     json_data = parse_xml_to_json(xml_path)

#     # Remove the XML file
#     os.remove(xml_path)

#     return json_data
    



