import os
import sys
import louis
# translate.py
from xml.etree.ElementTree import Element, SubElement, tostring

def quorum_to_blocks(code_input: str) -> str:
    from xml.etree.ElementTree import Element, SubElement, tostring

    root = Element("xml", xmlns="https://developers.google.com/blockly/xml")

    lines = code_input.splitlines()
    stack = [(0, root)]  # (indent_level, parent_element)

    def make_block(line):
        line = line.strip()
        if line.startswith("output"):
            block = Element("block", type="output")
            field = SubElement(block, "field", name="TEXT")
            msg = line[len("output"):].strip().strip('"')
            field.text = msg
            return block
        elif line.startswith("if"):
            block = Element("block", type="controls_if")
            # crude parse: "if true then"
            cond_value = SubElement(block, "value", name="IF0")
            bool_block = SubElement(cond_value, "block", type="logic_boolean")
            field = SubElement(bool_block, "field", name="BOOL")
            if "true" in line.lower():
                field.text = "TRUE"
            else:
                field.text = "FALSE"
            # add DO slot
            SubElement(block, "statement", name="DO0")
            return block
        elif line.startswith("repeat"):
            block = Element("block", type="controls_repeat_ext")
            times_value = SubElement(block, "value", name="TIMES")
            num_block = SubElement(times_value, "block", type="math_number")
            field = SubElement(num_block, "field", name="NUM")
            parts = line.split()
            if len(parts) >= 2 and parts[1].isdigit():
                field.text = parts[1]
            # add DO slot
            SubElement(block, "statement", name="DO")
            return block
        else:
            block = Element("block", type="quorum_statement")
            field = SubElement(block, "field", name="CODE")
            field.text = line
            return block

    prev_blocks_at_level = {}

    for raw_line in lines:
        if not raw_line.strip():
            continue
        indent = len(raw_line) - len(raw_line.lstrip(" "))
        block = make_block(raw_line)

        # find parent based on indentation
        while stack and indent < stack[-1][0]:
            stack.pop()

        parent_indent, parent_elem = stack[-1]

        if parent_elem.tag == "block" and parent_elem.get("type") in ("controls_if", "controls_repeat_ext"):
            # put inside statement if more indented
            if indent > parent_indent:
                stmt_name = "DO0" if parent_elem.get("type") == "controls_if" else "DO"
                stmt = parent_elem.find(f"statement[@name='{stmt_name}']")
                if stmt is not None and len(stmt) == 0:
                    stmt.append(block)
                else:
                    # chain inside statement
                    last = stmt[-1]
                    SubElement(last, "next").append(block)
                stack.append((indent, block))
                continue

        # otherwise, attach sequentially
        if isinstance(parent_elem, Element) and parent_elem.tag == "xml":
            if len(parent_elem) == 0:
                parent_elem.append(block)
            else:
                last = parent_elem[-1]
                SubElement(last, "next").append(block)
        elif parent_elem.tag == "block":
            # chain to previous block at same level
            if indent == parent_indent:
                SubElement(parent_elem, "next").append(block)
            else:
                parent_elem.append(block)

        stack.append((indent, block))

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
