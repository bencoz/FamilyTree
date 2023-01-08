import json
import xml.etree.ElementTree as ET


def keep_tags(xml_file, tags_to_keep):
    # Parse the XML file
    root = ET.parse(xml_file).getroot()

    # Iterate through all elements in the root
    for element in root.iter():
        # If the element is not in the list of tags to keep, remove it
        if element.tag not in tags_to_keep:
            element.clear()

    # Write the modified XML tree to a new file
    ET.ElementTree(root).write("modified.xml")
    root = ET.parse("modified.xml").getroot()
    # Create an empty dictionary to store the data
    data = {}

    # Iterate through the elements in the root
    for element in root:
        # Get the tag and text of the element
        tag = element.tag
        text = element.text

        # Add the data to the dictionary
        data[tag] = text

    # Convert the dictionary to a JSON object and return it
    return json.dumps(data)


# Test the function
w = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
j = keep_tags("xml_tree.xml", [w+"body", w+"p", w+"ilvl", w+"ilvl", w+"t", w+"pPr", w+"numPr", w+"r"])
print(j)