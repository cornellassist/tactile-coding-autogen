from pathlib import Path
import os
import sys
import subprocess
import xml.etree.ElementTree as ET
import json

#############
# Magic sauce
#############
def generate_with_template(text, file_name, block_type):
    base_dir = os.path.dirname(os.path.abspath(__file__))

    if block_type == "say":
        template_file = "say_block.scad"
    else:
        template_file = "action_block.scad"

    # point to your template/action_block.scad
    template_path = os.path.join(base_dir, "template", template_file)

    # single folder for both .scad and .stl
    scad_folder = os.path.join(base_dir, "scad_files")
    os.makedirs(scad_folder, exist_ok=True)

    # read template
    with open(template_path, "r", encoding="utf-8") as f:
        scad_code = f.read()

    # Escape text safely as a SCAD string
    safe_text = json.dumps(block_type)  # e.g. "This is my braille"
    scad_code = scad_code.replace('"// %%TEXT_PLACEHOLDER%%"', safe_text)

    # save SCAD file
    scad_script_path = os.path.join(scad_folder, file_name + ".scad")
    with open(scad_script_path, "w", encoding="utf-8") as f:
        f.write(scad_code)

    # run OpenSCAD → STL in the same folder
    openscad_executable = "/Applications/OpenSCAD.app/Contents/MacOS/OpenSCAD"
    subprocess.run([
        openscad_executable,
        "-o", os.path.join(scad_folder, file_name + ".stl"),
        scad_script_path
    ], check=True)

    print(f"Generated {file_name}.scad and {file_name}.stl in {scad_folder}")

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Generate SCAD + STL from template with input text")
    parser.add_argument("text", help="Input text to embed in the template")
    parser.add_argument("file_name", help="Base name for the output files (without extension)")

    args = parser.parse_args()

    generate_with_template(args.text, args.file_name)