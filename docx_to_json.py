import json
import docx
from docx.shared import Inches
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.enum.style import WD_STYLE_TYPE


def docx_to_json(docx_file):
    # Load the docx file
    doc = docx.Document(docx_file)

    # Initialize a list to store the JSON data
    data = []
    # body_element = doc._body._body
    # print(body_element.xml)
    # Iterate through the paragraphs in the docx file

    for p in doc.paragraphs:
        level = p.paragraph_format.left_indent
        name = p.text.strip()
        if level is None:
            print(name)
        item = {'level': level, 'text': name}
        data.append(item)

    # Convert the data list to a JSON string and return it
    # print(data)
    return json.dumps(data, indent=4)


# Example usage
docx_file = 'doc.docx'

json_data = docx_to_json(docx_file)
# print(json_data)
