import json
import re


def is_level_1_family(lst, curr_level):
    for i in range(1, len(lst)):
        if curr_level + 1 != lst[i]['level']:
            return False

    return True


def create_nested_json(lst, curr_level=0):
    # Base case: if the list is empty, return an empty dictionary
    if len(lst) == 0:
        return
    # One Person
    if len(lst) == 1:
        return {'name': lst[0]['name']}

    nested_json = {'name': lst[0]['name'], 'children': []}

    # Family with one level
    if is_level_1_family(lst, curr_level):
        for i in range(1, len(lst)):
            nested_json['children'].append(create_nested_json(lst[i:i+1], curr_level))
        return nested_json

    # Slice the list to hold the hierarchy
    next_item_level = lst[1]['level']
    if next_item_level > curr_level:
        # This is a child. Find all children i.e run until curr_level < next_item_level
        pos = 1
        for i in range(2, len(lst)):
            if next_item_level == lst[i]['level']:
                nested_json['children'].append(create_nested_json(lst[pos:i], curr_level + 1))
                pos = i
                if pos == len(lst) - 1 and lst[pos:i+1] is not None:
                    nested_json['children'].append(create_nested_json(lst[pos:i+1], curr_level + 1))
    return nested_json


def markdown_to_json(markdown_file):
    # Load the markdown file
    with open(markdown_file, 'r') as f:
        markdown = f.read()

    # Initialize a list to store the JSON data
    data = []

    # Iterate through the lines in the markdown file
    for line in markdown.split('\n'):
        # Extract the list level and name from the line
        match = re.match(r'^(\s*)([^\s].*?)$', line)
        if match:
            level = len(match.group(1)) // 2
            name = match.group(2)

            # Remove HTML tags from the name
            name = re.sub(r'<[^>]*>', '', name).replace("- ", "")

            # Add a new object to the data list for the list item
            item = {'level': level, 'name': name}
            data.append(item)

    # Nest the JSON data by level
    root = create_nested_json(data)
    return json.dumps(root, indent=4)


# Example usage
markdown_file = 'somedoc.md'
json_data = markdown_to_json(markdown_file)
print(json_data)
