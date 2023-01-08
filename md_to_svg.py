import re
import numpy as np

from xml.etree import ElementTree as ET

node_width = 200
node_height = 75
child_spacing = 500
child_y_offset = 250
text_y_offset = 50


def create_svg(json_data, parent_x=0, parent_y=0, x=0, y=0, level=0, nodes=[]):
    # Create the main rectangle for this node
    rect = ET.Element("rect", {
        "x": str(x),
        "y": str(y),
        "width": str(node_width),
        "height": str(node_height),
        "fill": "#ffffff",
        "stroke": "#000000"
    })

    # Create the text element for this node
    text = ET.Element("text", {
        "x": str(x + node_width / 2),
        "y": str(y + text_y_offset),
        "font-size": "20",
        "text-anchor": "middle"
    })
    text.text = json_data["name"]

    # Create a group to hold the rectangle, text, and arrow elements
    group = ET.Element("g")
    group.append(rect)
    group.append(text)

    # Add this node to the list of nodes
    nodes.append((x, y, node_width, node_height))

    # Recursively create the child nodes
    children = json_data.get("children", [])
    num_children = len(children)
    if num_children > 0:
        # Calculate the spacing between the children
        total_child_width = (num_children - 1) * child_spacing
        for i, child in enumerate(children):
            # Calculate the initial position of the child node
            child_x = x - total_child_width / 2 + i * child_spacing
            child_y = y + child_y_offset



            # Create the child node
            child_group = create_svg(child, x, y, child_x, child_y, level + 1, nodes)

            # Calculate the coordinates of the arrow
            arrow_x1 = x + node_width / 2
            arrow_y1 = y + node_height
            arrow_x2 = child_x + node_width / 2
            arrow_y2 = child_y

            # Create the arrow line
            arrow = ET.Element("line", {
                "x1": str(arrow_x1),
                "y1": str(arrow_y1),
                "x2": str(arrow_x2),
                "y2": str(arrow_y2),
                "stroke": "#000000"
            })

            # Add the arrow and child group to the parent group
            group.append(arrow)
            group.append(child_group)

    return group


def calculate_tree_dimensions(json_data, x=0, y=0, level=0):
    # Initialize the dimensions of the tree
    tree_width = node_width
    tree_min_x = x
    tree_max_x = x
    tree_height = node_height

    # Recursively calculate the dimensions of the child nodes
    children = json_data.get("children", [])
    num_children = len(children)
    if num_children > 0:
        # Calculate the spacing between the children
        total_child_width = (num_children - 1) * child_spacing
        for i, child in enumerate(children):
            child_x = x - total_child_width / 2 + i * child_spacing
            child_width, child_min_x, child_max_x, child_height = calculate_tree_dimensions(child, child_x,
                                                                                            y + child_y_offset,
                                                                                            level + 1)

            # Update the dimensions of the tree
            tree_min_x = min(tree_min_x, child_min_x)
            tree_max_x = max(tree_max_x, child_max_x)
            tree_width = tree_max_x - tree_min_x
            tree_height = max(tree_height, y + child_y_offset + child_height - y)

    return tree_width, tree_min_x, tree_max_x, tree_height


def generate_svg(json_data, filename, padding=50, max_width=1500):
    # Calculate the dimensions of the tree
    tree_width, tree_min_x, tree_max_x, tree_height = calculate_tree_dimensions(json_data)

    # Calculate the scaling factor to fit the tree within the maximum width
    scale = min(1, max_width / tree_width)

    # Calculate the dimensions of the SVG element
    svg_width = tree_width + padding * 2
    svg_height = tree_height + padding * 2

    # Calculate the translation needed to center the tree within the SVG element
    translate_x = padding - tree_min_x
    translate_y = padding

    # Create the SVG element
    svg = ET.Element("svg", {
        "width": str(svg_width),
        "height": str(svg_height),
        "xmlns": "http://www.w3.org/2000/svg",
    })

    # Create the root group
    root_group = ET.Element("g", {
        "transform": f"translate({translate_x}, {translate_y}) scale({scale})"
    })

    # Create the main tree from the JSON data
    tree_group = create_svg(json_data)

    # Add the tree to the root group
    root_group.append(tree_group)

    # Add the root group to the SVG element
    svg.append(root_group)

    # Write the SVG element to the file
    tree = ET.ElementTree(svg)
    tree.write(filename)


def do_split(lst, slices):
    return [sl.tolist() for sl in np.split(lst, slices)]


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
            nested_json['children'].append(create_nested_json(lst[i:i + 1], curr_level + 1))
        return nested_json

    # Find siblings
    next_item_level = curr_level + 1
    siblings_indx = []
    children_list = lst[1:]
    for i in range(1, len(children_list)):
        if next_item_level == children_list[i]['level']:
            siblings_indx.append(i)

    if len(siblings_indx) > 0:
        siblings = do_split(children_list, siblings_indx)
        for sibling in siblings:
            nested_json['children'].append(create_nested_json(sibling, curr_level + 1))
    else:
        nested_json['children'].append(create_nested_json(children_list, curr_level + 1))

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
    return root


markdown_file = './family_tree.md'
family_dict = markdown_to_json(markdown_file)
generate_svg(family_dict, "family_tree.svg")
