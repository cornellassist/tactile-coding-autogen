from pathlib import Path
import os
import sys
import subprocess
import xml.etree.ElementTree as ET
import json

#############
# Magic sauce
#############
def add_block_to_palette(file_name):
    home_dir = Path.home()
    palette_path = home_dir / "CAT" / "TactileCode" / "brailleGen" / "WebBlockEditor" / "palette.xml"
    tree = ET.parse(palette_path)
    root = tree.getroot()

    # Find or create a "Custom" category
    category = None
    for cat in root.findall("category"):
        if cat.get("name") == "Custom":
            category = cat
            break
    if category is None:
        category = ET.SubElement(root, "category", {"name": "Custom"})

    # Create the new block for this STL
    new_block = ET.SubElement(category, "block", {"type": "brailleTile"})
    field = ET.SubElement(new_block, "field", {"name": "TEXT"})
    field.text = file_name
    
    # Save updated XML
    tree.write(palette_path, encoding="utf-8", xml_declaration=True)
    print(f"Added brailleTile block for {file_name} to palette.xml")

def wrap_text(text, chars_per_line):
    words = text.split('⠀')  # Split the text into words
    lines = []  # List to store wrapped lines
    current_line = []  # Current line being constructed
    current_length = 0  # Length of the current line

    for word in words:
        # Check if adding the word exceeds the limit
        if current_length + len(word) + len(current_line) > chars_per_line:
            # Add the current line to lines and start a new line
            lines.append('⠀'.join(current_line))
            current_line = [word]
            current_length = len(word)
        else:
            # Add the word to the current line
            current_line.append(word)
            current_length += len(word)

    # Add the last line if it contains words
    if current_line:
        lines.append('⠀'.join(current_line))

    return lines

def generate_with_template(text, file_name):
    base_dir = os.path.dirname(os.path.abspath(__file__))

    # point to your template/action_block.scad
    template_path = os.path.join(base_dir, "template", "action_block.scad")

    # single folder for both .scad and .stl
    scad_folder = os.path.join(base_dir, "scad_files")
    os.makedirs(scad_folder, exist_ok=True)

    # read template
    with open(template_path, "r", encoding="utf-8") as f:
        scad_code = f.read()

    # Escape text safely as a SCAD string
    safe_text = json.dumps(text)  # e.g. "This is my braille"
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

def generate(translation, cpl, bh, ph, ms, es, file_name):
    openscad_executable = "/Applications/OpenSCAD.app/Contents/MacOS/OpenSCAD"

    if getattr(sys, 'frozen', False):  # Running as an executable
        base_dir = os.path.dirname(sys.executable)
    else:  # Running as a script
        base_dir = os.path.dirname(os.path.abspath(__file__))

    # Define the output folder
    output_folder = os.path.join(base_dir, 'output files')

    wrapped_text = wrap_text(translation, cpl)

    # Convert translation to 2D arrays for OpenSCAD
    braille_dict = {
        "⠀": [[0, 0, 0], [0, 0, 0]], #2800
        "⠁": [[1, 0, 0], [0, 0, 0]], #2801
        "⠂": [[0, 1, 0], [0, 0, 0]], #2802
        "⠃": [[1, 1, 0], [0, 0, 0]], #2803
        "⠄": [[0, 0, 1], [0, 0, 0]], #2804
        "⠅": [[1, 0, 1], [0, 0, 0]], #2805
        "⠆": [[0, 1, 1], [0, 0, 0]], #2806
        "⠇": [[1, 1, 1], [0, 0, 0]], #2807
        "⠈": [[0, 0, 0], [1, 0, 0]], #2808
        "⠉": [[1, 0, 0], [1, 0, 0]], #2809
        "⠊": [[0, 1, 0], [1, 0, 0]], #280A
        "⠋": [[1, 1, 0], [1, 0, 0]], #280B
        "⠌": [[0, 0, 1], [1, 0, 0]], #280C
        "⠍": [[1, 0, 1], [1, 0, 0]], #280D
        "⠎": [[0, 1, 1], [1, 0, 0]], #280E
        "⠏": [[1, 1, 1], [1, 0, 0]], #280F
        "⠐": [[0, 0, 0], [0, 1, 0]], #2810
        "⠑": [[1, 0, 0], [0, 1, 0]], #2811
        "⠒": [[0, 1, 0], [0, 1, 0]], #2812
        "⠓": [[1, 1, 0], [0, 1, 0]], #2813
        "⠔": [[0, 0, 1], [0, 1, 0]], #2814
        "⠕": [[1, 0, 1], [0, 1, 0]], #2815
        "⠖": [[0, 1, 1], [0, 1, 0]], #2816
        "⠗": [[1, 1, 1], [0, 1, 0]], #2817
        "⠘": [[0, 0, 0], [1, 1, 0]], #2818
        "⠙": [[1, 0, 0], [1, 1, 0]], #2819
        "⠚": [[0, 1, 0], [1, 1, 0]], #281A
        "⠛": [[1, 1, 0], [1, 1, 0]], #281B
        "⠜": [[0, 0, 1], [1, 1, 0]], #281C
        "⠝": [[1, 0, 1], [1, 1, 0]], #281D
        "⠞": [[0, 1, 1], [1, 1, 0]], #281E
        "⠟": [[1, 1, 1], [1, 1, 0]], #281F
        "⠠": [[0, 0, 0], [0, 0, 1]], #2820
        "⠡": [[1, 0, 0], [0, 0, 1]], #2821
        "⠢": [[0, 1, 0], [0, 0, 1]], #2822
        "⠣": [[1, 1, 0], [0, 0, 1]], #2823
        "⠤": [[0, 0, 1], [0, 0, 1]], #2824
        "⠥": [[1, 0, 1], [0, 0, 1]], #2825
        "⠦": [[0, 1, 1], [0, 0, 1]], #2826
        "⠧": [[1, 1, 1], [0, 0, 1]], #2827
        "⠨": [[0, 0, 0], [1, 0, 1]], #2828
        "⠩": [[1, 0, 0], [1, 0, 1]], #2829
        "⠪": [[0, 1, 0], [1, 0, 1]], #282A
        "⠫": [[1, 1, 0], [1, 0, 1]], #282B
        "⠬": [[0, 0, 1], [1, 0, 1]], #282C
        "⠭": [[1, 0, 1], [1, 0, 1]], #282D
        "⠮": [[0, 1, 1], [1, 0, 1]], #282E
        "⠯": [[1, 1, 1], [1, 0, 1]], #282F
        "⠰": [[0, 0, 0], [0, 1, 1]], #2830
        "⠱": [[1, 0, 0], [0, 1, 1]], #2831
        "⠲": [[0, 1, 0], [0, 1, 1]], #2832
        "⠳": [[1, 1, 0], [0, 1, 1]], #2833
        "⠴": [[0, 0, 1], [0, 1, 1]], #2834
        "⠵": [[1, 0, 1], [0, 1, 1]], #2835
        "⠶": [[0, 1, 1], [0, 1, 1]], #2836
        "⠷": [[1, 1, 1], [0, 1, 1]], #2837
        "⠸": [[0, 0, 0], [1, 1, 1]], #2838
        "⠹": [[1, 0, 0], [1, 1, 1]], #2839
        "⠺": [[0, 1, 0], [1, 1, 1]], #283A
        "⠻": [[1, 1, 0], [1, 1, 1]], #283B
        "⠼": [[0, 0, 1], [1, 1, 1]], #283C
        "⠽": [[1, 0, 1], [1, 1, 1]], #283D
        "⠾": [[0, 1, 1], [1, 1, 1]], #283E
        "⠿": [[1, 1, 1], [1, 1, 1]] #283F
    }

    the_matrix = []
    for line in wrapped_text:
        current_line = []
        for char in line:
            current_line.append(braille_dict.get(char, [[0, 0, 0], [0, 0, 0]]))
        the_matrix.append(current_line)

    # Create folders for SCAD and STL files
    scad_folder = os.path.join(base_dir, 'scad_files')
    output_folder = os.path.join(base_dir, 'output_files')
    os.makedirs(scad_folder, exist_ok=True)
    os.makedirs(output_folder, exist_ok=True)

    # Assign SCAD file path
    scad_script_path = os.path.join(scad_folder, file_name + ".scad")

    scad_code = f"""
    the_matrix = {the_matrix};

    export_scale = {es}; //USER INPUT

    diameter = 1.6;
    radius = diameter / 2;
    braille_height = {bh}; //USER INPUT
    fillet_radius = .4;

    spacing = 2.54;
    distance = 6.2; // horizontal braille cell spacing

    // define braille starting position
    letfc = 2; // left edge to first column of braille
    line_margin = {ms}; //USER INPUT

    // define plate size
    plate_height = {ph}; //USER INPUT
    plate_depth = spacing * 2 + diameter + line_margin * 2; // x axis dimension

    // braille dot revolve profile points
    points = concat([[0,braille_height],[0,0],[radius,0]],[for(a = [0:18:90]) [fillet_radius * cos(a) + radius-fillet_radius, fillet_radius * sin(a) + braille_height-fillet_radius]]);

    scale([export_scale, export_scale, export_scale]) {{
        rotate([0,0,-90]) {{
            for (line = [0:len(the_matrix) - 1]) {{
                for (char_index = [0:len(the_matrix[line]) - 1]) {{
                    current_char = the_matrix[line][char_index];
                    braille_points(line, char_index, current_char);
                }}
            }}
        }}
    }}

    // braille_str transforms each braille character into its position on the plate
    module braille_points(line, index, bitmap) {{
        plate_length = (distance * len(the_matrix[line])) + letfc * 2 - diameter;
        
        union() {{
            color([19/255,56/255,190/255]) {{ //preview color, blue 
                cube([plate_depth * (line+1), plate_length, plate_height]); //rectangular prism backing the braille
            }}
            
            translate([line_margin + plate_depth * line, distance * index + letfc, plate_height]) {{
                for (col = [0:1]) {{
                    for (row = [0:2]) {{
                        if (bitmap[col][row] == 1) {{
                            translate([spacing * (row) + radius, spacing * (col) + radius, 0]) {{
                                rotate_extrude($fn = 20) // revolve each braille dot
                                    polygon(points);
                            }}
                        }}
                    }}
                }}
            }}
        }}
    }}
    """

    with open(scad_script_path, 'w', encoding='utf-8') as file:
        file.write(scad_code)

    subprocess.run([
    openscad_executable,
    "--backend=manifold",
    "-o", os.path.join(output_folder, file_name+".stl"),
    scad_script_path
], check=True)
    add_block_to_palette(file_name)

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Generate SCAD + STL from template with input text")
    parser.add_argument("text", help="Input text to embed in the template")
    parser.add_argument("file_name", help="Base name for the output files (without extension)")

    args = parser.parse_args()

    generate_with_template(args.text, args.file_name)