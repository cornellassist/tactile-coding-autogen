import os
import sys
import louis
# translate.py
from xml.etree.ElementTree import Element, SubElement, tostring

def quorum_to_blocks(code_input: str) -> str:
    root = Element("xml")

    for line in code_input.splitlines():
        line = line.strip()
        if not line:
            continue

        if line.startswith("output"):
            block = SubElement(root, "block", type="output")
            field = SubElement(block, "field", name="TEXT")
            msg = line[len("output"):].strip().strip('"')
            field.text = msg

        elif line.startswith("integer"):
            parts = line.split("=")
            if len(parts) == 2:
                decl = parts[0].strip().split()
                if len(decl) >= 2:
                    var_name = decl[1]
                    value = parts[1].strip()
                    block = SubElement(root, "block", type="variable_declare")
                    var_field = SubElement(block, "field", name="VAR")
                    var_field.text = var_name
                    val_field = SubElement(block, "field", name="VALUE")
                    val_field.text = value

        elif line.startswith("if"):
            block = SubElement(root, "block", type="if_block")
            cond = line[len("if"):].strip()
            if cond.endswith("then"):
                cond = cond[:-len("then")].strip()
            field = SubElement(block, "field", name="COND")
            field.text = cond

        elif line.startswith("repeat"):
            # repeat 5 times
            block = SubElement(root, "block", type="repeat_block")
            field = SubElement(block, "field", name="COUNT")
            parts = line.split()
            if len(parts) >= 2 and parts[1].isdigit():
                field.text = parts[1]
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
