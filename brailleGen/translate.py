import os
import sys
import louis
# translate.py
from xml.etree.ElementTree import Element, SubElement, tostring

def quorum_to_blocks(code_input: str) -> str:
    root = Element("xml", xmlns="https://developers.google.com/blockly/xml")


    for line in code_input.splitlines():
        line = line.strip()
        if not line:
            continue

        if line.startswith("output"):
            block = SubElement(root, "block", type="output")
            field = SubElement(block, "field", name="TEXT")
            # capture text inside quotes
            msg = line[len("output"):].strip().strip('"')
            field.text = msg
        elif line.startswith("repeat"):
            block = SubElement(root, "block", type="repeat")
            field = SubElement(block, "field", name="TIMES")
            # crude parse "repeat 5 times"
            parts = line.split()
            if len(parts) >= 2 and parts[1].isdigit():
                field.text = parts[1]
        else:
            block = SubElement(root, "block", type="quorum_statement")
            field = SubElement(block, "field", name="CODE")
            field.text = line

    return tostring(root, encoding="unicode")


def louis_translate(text_input, table, file_name):
    # Check if running as a script or as a frozen executable
    if getattr(sys, 'frozen', False):  # Running as an executable
        base_dir = os.path.dirname(sys.executable)
        table_folder = os.path.join(base_dir, '_internal', 'tables')
    else:  # Running as a script
        base_dir = os.path.dirname(os.path.abspath(__file__))
        table_folder = os.path.join(base_dir, 'liblouis', 'tables')  # Adjust path as per your project structure

    dots_path = os.path.join(table_folder, "braille-patterns.cti")
    table_path = os.path.join(table_folder, table)
    
    # Ensure the paths exist before attempting to use them
    if not os.path.exists(dots_path):
        raise RuntimeError(f"Cannot resolve dots file at {dots_path}")
    
    if not os.path.exists(table_path):
        raise RuntimeError(f"Cannot resolve table file at {table_path}")

    # Translate the input text using Louis
    try:
        translation = louis.translateString([dots_path, table_path], text_input)
    except RuntimeError as e:
        raise RuntimeError(f"Error during translation: {str(e)}")

    output_folder = os.path.join(base_dir, 'output files')

    # Create the folder if it doesn't exist
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # Save the translation to a file
    output_file = os.path.join(output_folder, file_name + ".txt")
    with open(output_file, "w", encoding="utf-8") as file:
        file.write(table + "\n" + text_input + "\n" + translation)
    
    # Convert translation into XML format for Blockly
    root = Element('xml')
    block = SubElement(root, 'block', type="brailleTile")
    field = SubElement(block, 'field', name="TEXT")
    field.text = translation
    
    # Return XML string
    return tostring(root, encoding="unicode")
