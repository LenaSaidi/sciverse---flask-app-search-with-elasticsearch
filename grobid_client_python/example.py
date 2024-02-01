import os
import xml.etree.ElementTree as ET

def parse_xml_to_json(xml_content):
    root = ET.fromstring(xml_content)

    def extract_authors(element):
        authors = []
        for author_element in element.findall('.//tei:author', namespaces={'tei': 'http://www.tei-c.org/ns/1.0'}):
            name = author_element.findtext('tei:persName/tei:surname', '', namespaces={'tei': 'http://www.tei-c.org/ns/1.0'})
            email = author_element.findtext('tei:email', '', namespaces={'tei': 'http://www.tei-c.org/ns/1.0'})

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

    data = {
        'title': root.findtext('.//tei:titleStmt/tei:title[@type="main"]', '', namespaces={'tei': 'http://www.tei-c.org/ns/1.0'}),
        'abstract': extract_abstract(root),
        'authors': extract_authors(root),
        'keywords': extract_keywords(root),
        'references': extract_references(root),
        'full_text': extract_full_text(root),
    }

    return data

def JsonGenr(pdf_path, xml_path):
    with open(xml_path, 'r', encoding='utf-8') as xml_file:
        xml_content = xml_file.read()

    json_data = parse_xml_to_json(xml_content)
    os.remove(xml_path)

    return json_data

# Call the method
if __name__ == "__main__":
    current_dir = os.path.dirname(os.path.abspath(__file__))
    pdf_path = os.path.join(current_dir, 'grobid_client_python/tests/test_pdf/test.pdf')  
    xml_path = os.path.join(current_dir, 'tests', 'test_out', 'test.grobid.tei.xml')

    json_data = JsonGenr(pdf_path, xml_path)
    print(json_data)
