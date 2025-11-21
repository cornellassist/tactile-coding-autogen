from pathlib import Path
import os
import subprocess
import json
import shutil

#############
# Magic sauce
#############
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

def generate_with_template(braille, text, file_name, cpl=20):
    base_dir = os.path.dirname(os.path.abspath(__file__))

    # single folder for both .scad and .stl
    scad_folder = os.path.join(base_dir, "scad_files")
    os.makedirs(scad_folder, exist_ok=True)

    # --- Clear old files ---
    for f in Path(scad_folder).glob("*"):
        try:
            f.unlink()
        except IsADirectoryError:
            shutil.rmtree(f)

    # process each line separately
    for i, line in enumerate(text.splitlines(), start=1):
        line = line.strip()
        if not line:
            continue  # skip blank lines

        # first word = block type, rest = text
        parts = line.split(maxsplit=1)
        block_type = parts[0]
        block_text = parts[1] if len(parts) > 1 else ""

        # filenames per line
        scad_name = f"{file_name}.scad"
        stl_name = f"{file_name}.stl"

        scad_path = os.path.join(scad_folder, scad_name)
        stl_path = os.path.join(scad_folder, stl_name)
    
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

    # wrap braille string into lines
    wrapped_text = wrap_text(braille, chars_per_line=cpl)

    # convert each line into bitmaps
    the_matrix = []
    for line in wrapped_text:
        current_line = []
        for char in line:
            current_line.append(braille_dict.get(char, [[0, 0, 0], [0, 0, 0]]))
        the_matrix.append(current_line)

    say_scad_code = f"""
    the_matrix = {the_matrix};

export_scale = 1; //USER INPUT
diameter = 1.6;
radius = diameter / 2;
braille_height = 0.6; //USER INPUT
fillet_radius = .4;
spacing = 2.54;
distance = 6.2; // horizontal braille cell spacing
// define braille starting position
letfc = 2; // left edge to first column of braille
line_margin = 1; //USER INPUT
// define plate size
plate_height = 0; //USER INPUT
plate_depth = spacing * 2 + diameter + line_margin * 2; // x axis dimension
depth = 3.6;
leg = 9.19;
top_width = 14;
block_width = 21.972;
connector_side_length = 28.849;
connector_start_x = 100 + connector_side_length;
connector_trapezoid_width = 22.039;
// braille dot revolve profile points
points = concat([[0,braille_height],[0,0],[radius,0]],[for(a = [0:18:90]) [fillet_radius * cos(a) + radius-fillet_radius, fillet_radius * sin(a) + braille_height-fillet_radius]]);
scale([export_scale, export_scale, export_scale]) {{
    rotate([0,0,-90]) {{
        for (line = [0:len(the_matrix) - 1]) {{
            for (char_index = [0:len(the_matrix[line]) - 1]) {{
                current_char = the_matrix[line][char_index];
                braille_points(line, char_index, current_char, top_width, connector_side_length);
            }}
        }}
    }}
}}
// braille_str transforms each braille character into its position on the plate
module braille_points(line, index, bitmap, top_width, connector_side_length) {{
    plate_length = (distance * len(the_matrix[line])) + letfc * 2 - diameter;
    start = ((4*leg+3*top_width) - plate_length)/2;
    union() {{
        color([19/255,56/255,190/255]) {{ //preview color, blue
            cube([plate_depth * (line+1), plate_length, plate_height]); //rectangular prism backing the braille
        }}
        color("white")
        translate([line_margin + plate_depth * line + top_width + 2, distance * index + letfc + start, depth]) {{
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
module block_trapezoid (depth, leg_x, leg_y, top_width, left_bottom_x, left_bottom_y) {{
color("black")
linear_extrude(depth)
polygon(
    points=[
        [left_bottom_x, left_bottom_y],  // Bottom left corner
        [left_bottom_x + leg_x, left_bottom_y + leg_y], // Top left corner
        [left_bottom_x + leg_x + top_width, left_bottom_y + leg_y], // Top right corner
        [left_bottom_x + top_width + 2*(leg_x), left_bottom_y]   // Bottom right corner
    ]
);
}}
module block_rectangle (depth, leg, top_width, block_width, text) {{
plate = [3*(top_width) + 4*(leg), block_width, depth]; // Block
translate([0, -block_width, 0])
color("black")
cube(plate);
color("white")
linear_extrude(3*depth/2)
translate([(3*(top_width) + 4*(leg))/2, -2*block_width/3, 0])
text( text, size = 6, halign = "center");
}}
module connector_trapezoid (depth, leg, top_width, block_width) {{
color("black")
linear_extrude(depth / 2)
polygon(
    points=[
        [3*(top_width) + 4*(leg), -(2*block_width)/3],  // Top left corner
        [3*(top_width) + 4*(leg), -(block_width)/3], // Top right corner
        [3*(top_width) + 4*(leg) + 6.004154, -((block_width)/3) + 3.4665], // Bottom right corner
        [3*(top_width) + 4*(leg) + 6.004154, -((2*block_width)/3) - 3.4665]   // Bottom left corner
    ]
);
}}
module top_triangle (depth, leg, start_x, start_y)
linear_extrude(depth)
polygon(
    points=[
        [start_x, start_y],
        [start_x + leg, start_y - leg],
        [start_x + leg, start_y],
    ]
);
module bot_triangle (depth, leg, start_x, start_y)
linear_extrude(depth)
polygon(
    points=[
        [start_x, start_y],
        [start_x + leg, start_y],
        [start_x + leg, start_y + leg],
    ]
);
module block_connector (depth, leg, top_width, width, height, start_x) {{
difference() {{
    plate = [width + leg, height + 2*(leg), depth];
    translate([3*(top_width) + 4*(leg) + 21.24, -height-leg, 0])
    color("black")
    cube(plate);
    translate([0.02, 0.02, -0.02])
    color("black")
    top_triangle(depth *2, leg, start_x, leg);
    color("black")
    translate([0.02, -0.02, -0.02])
    bot_triangle(depth *2, leg, start_x, -height-leg);
    translate([-0.02, 0.02, -0.02])
    color("black")
    linear_extrude(depth*2)
    polygon(
        points=[
            [3*(top_width) + 5*(leg) + 21.24, 0],  // Top left corner
            [3*(top_width) + 5*(leg) + 21.24, -21.945], // Top right corner
            [3*(top_width) + 4*(leg) + 21.24, -height-leg], // Bottom right corner
            [3*(top_width) + 4*(leg) + 21.24, leg]   // Bottom left corner
        ]
    );
    translate([-0.02, 0.02, -0.02])
    color("white")
    linear_extrude(depth / 2) // Connector Trapezoid
    polygon(
        points=[
            [3*(top_width) + 5*(leg) + 21.24, (-2*21.945)/3],  // Top left corner
            [3*(top_width) + 5*(leg) + 21.24, (-21.945)/3], // Top right corner
            [3*(top_width) + 5*(leg) + 21.24 + 6.27868, (-21.945)/3 + 3.625], // Bottom right corner
            [3*(top_width) + 5*(leg) + 21.24 + 6.27868, (-2*21.945)/3 - 3.625]   // Bottom left corner
        ]
    );
}}
}}
block_trapezoid(depth, leg, leg, top_width, 0, 0); // Top Left Trapezoid
block_trapezoid(depth, leg, leg, top_width, 2*(top_width) + 2*(leg), 0); // Top Right Trapezoid
block_rectangle(depth, leg, top_width, block_width, "say"); // Rectangle Block
block_trapezoid(depth, leg, -leg, top_width, 0, -block_width); // Bottom Left Trapezoid
block_trapezoid(depth, leg, -leg, top_width, 2*(top_width)+ 2*(leg), -block_width); // Bottom Right Trapezoid
block_trapezoid(depth, leg, leg, top_width, top_width + leg, -block_width-leg); // Top Half Hexagon
block_trapezoid(depth, leg, -leg, top_width, top_width + leg, -block_width-leg); // Bottom Half Hexagon
connector_trapezoid(depth / 2, leg, top_width, block_width); // Connector Trapezoid
block_connector(depth, leg, top_width, connector_side_length, connector_trapezoid_width, connector_start_x);
    """
    action_scad_code = f"""
the_matrix = {the_matrix};
export_scale = 1; //USER INPUT

    diameter = 1.6;
    radius = diameter / 2;
    braille_height = 0.6; //USER INPUT
    fillet_radius = .4;

    spacing = 2.54;
    distance = 6.2; // horizontal braille cell spacing

    // define braille starting position
    letfc = 2; // left edge to first column of braille
    line_margin = 1; //USER INPUT

    // define plate size
    plate_height = 0; //USER INPUT
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
            color("white")
            translate([(leg+top_width)/2, distance * index + leg/2, depth]) {{
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
module horiz_trapezoid (depth, leg_x, leg_y, top_width, left_bottom_x, left_bottom_y) {{
color("black")
linear_extrude(depth)
polygon(
    points=[
        [left_bottom_x, left_bottom_y],  // Bottom left corner
        [left_bottom_x + leg_x, left_bottom_y + leg_y], // Top left corner
        [left_bottom_x + leg_x + top_width, left_bottom_y + leg_y], // Top right corner
        [left_bottom_x + top_width + 2*(leg_x), left_bottom_y]   // Bottom right corner
    ]
);
}}
module vert_trapezoid (depth, leg_x, leg_y, top_width, left_bottom_x, left_bottom_y) {{
    color("black")
    linear_extrude(depth)
    polygon(
        points=[
            [left_bottom_x, left_bottom_y],  // Bottom left corner
            [left_bottom_x + leg_x, left_bottom_y - leg_y], // Top left corner
            [left_bottom_x + leg_x, left_bottom_y - leg_y - top_width], // Top right corner
            [left_bottom_x, left_bottom_y - (top_width + 2*(leg_x))]   // Bottom right corner
        ]
    );
}}
module text_rectangle (depth, block_width, block_length, text) {{
    plate = [block_length, block_width, depth]; // Block
    translate([0, -block_width, 0])
    color("black")
    cube(plate);
    color("white")
    linear_extrude(3*depth/2)
    translate([leg+(top_width/2),-1*leg,0])
    text( text, size = 6, halign = "center");
    
}}
module block_rectangle (depth, block_width, block_length, start_x, start_y) {{
    plate = [block_length, block_width, depth]; // Block
    translate([start_x, start_y, 0])
    color("black")
    cube(plate);
}}
module indent_rectangle (depth, leg, width_down, block_width, block_length, start_x, start_y) {{
    plate1 = [block_length, block_width, depth]; // Block
    plate2 = [69, 22, depth / 2];
    
    difference() {{
        translate([start_x, start_y, 0])
        color("black")
        cube(plate1);
        
        translate([0.2, 0.2, 0.2])
        translate([start_x+leg/2, -width_down-leg/4, depth/2])
        color("white")
        cube(plate2);  
     }}
    
}}
module bot_triangle (depth, leg, start_x, start_y)
    color("black")
    linear_extrude(depth)
    polygon(
        points=[
            [start_x, start_y],
            [start_x, start_y - leg],
            [start_x + leg, start_y], 
        ]
    );
module top_triangle (depth, leg, start_x, start_y)
    color("black")
    linear_extrude(depth)
    polygon(
        points=[
            [start_x, start_y],
            [start_x + leg, start_y],
            [start_x + leg, start_y + leg], 
        ]      
 );
depth = 3.6;
leg = 9.19;
top_width = 14;
vert_trap_top_width = 17.939;
text_block_width = 46.319;
text_block_length = leg + top_width + leg;
mid_block_width = vert_trap_top_width + leg;
mid_block_length = leg + top_width;
big_block_width = vert_trap_top_width +(2*leg);
big_block_length = 76.835;
horiz_trapezoid(depth, leg, leg, top_width, 0, 0); // Top Left Trapezoid
text_rectangle (depth, text_block_width, text_block_length, "action"); // Block with Text
horiz_trapezoid (depth, leg, -leg, top_width, 0, -text_block_width); // Bottom Left Trapezoid
block_rectangle (depth, mid_block_width, mid_block_length, text_block_length, -mid_block_width); // Mid Block 
top_triangle (depth, leg, text_block_length + top_width, 0); // Top Triangle
bot_triangle (depth, leg, text_block_length, -mid_block_width); // Bot Triangle
indent_rectangle (depth, leg, vert_trap_top_width, big_block_width, big_block_length, text_block_length + top_width + leg,-big_block_width+leg); // Big Block
vert_trapezoid (depth, leg, leg, vert_trap_top_width, text_block_length + top_width + leg + big_block_length, leg); 
horiz_trapezoid (depth, leg, -leg, top_width, 3*(leg) + 2*(top_width), -vert_trap_top_width-leg); // Bottom Right Trapezoid
    """
    end_scad_code = f"""
    the_matrix = {the_matrix};
    export_scale = 1; //USER INPUT

    diameter = 1.6;
    radius = diameter / 2;
    braille_height = 0.6; //USER INPUT
    fillet_radius = .4;

    spacing = 2.54;
    distance = 6.2; // horizontal braille cell spacing

    // define braille starting position
    letfc = 2; // left edge to first column of braille
    line_margin = 1; //USER INPUT

    // define plate size
    plate_height = 0; //USER INPUT
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
            color("white")
            translate([(leg+top_width)/2, distance * index + leg + 6*top_width/7, depth]) {{
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
module horiz_trapezoid (depth, leg_x, leg_y, top_width, left_bottom_x, left_bottom_y) {{
    color("black")
    linear_extrude(depth)
    polygon(
        points=[
            [left_bottom_x, left_bottom_y],  // Bottom left corner
            [left_bottom_x + leg_x, left_bottom_y + leg_y], // Top left corner
            [left_bottom_x + leg_x + top_width, left_bottom_y + leg_y], // Top right corner
            [left_bottom_x + top_width + 2*(leg_x), left_bottom_y]   // Bottom right corner
        ]
    );
}}

module vert_trapezoid (depth, leg_x, leg_y, top_width, left_bottom_x, left_bottom_y) {{
    color("black")
    linear_extrude(depth)
    polygon(
        points=[
            [left_bottom_x, left_bottom_y],  // Bottom left corner
            [left_bottom_x + leg_x, left_bottom_y - leg_y], // Top left corner
            [left_bottom_x + leg_x, left_bottom_y - leg_y - top_width], // Top right corner
            [left_bottom_x, left_bottom_y - (top_width + 2*(leg_x))]   // Bottom right corner
        ]
    );
}}

module text_rectangle (depth, block_width, block_length, text) {{
    start_x = 3*(leg)+2*(top_width);
    difference() {{
        plate = [block_length, block_width, depth]; // Block
        translate([0, -block_width, 0])
        color("black")
        cube(plate);
    
        translate([0.02, 0.02, -0.2])
        color("black")
        horiz_trapezoid (depth*2, leg, -leg, top_width, start_x, 0);
        
        translate([-0.02, -0.02, -0.2])
        color("black")
        top_triangle (depth*2, leg, 0, -text_block_width);
    }}
    
    color("white")
    linear_extrude(3*depth/2)
    translate([leg+top_width+leg/3, -leg, 0])
    text( text, size = 6, halign = "center");
}}

module block_rectangle (depth, block_width, block_length, start_x, start_y) {{

    difference() {{
        plate = [block_length, block_width, depth]; // Block
        translate([start_x, start_y, 0])
        color("black")
        cube(plate);
    
        translate([0.02, 0.02, -0.2])
        color("black")
        horiz_trapezoid (depth*2, leg, -leg, top_width, 0,  top_block_width);
    }}
}}

module bot_triangle (depth, leg, start_x, start_y)
    color("black")
    linear_extrude(depth)
    polygon(
        points=[
            [start_x, start_y],
            [start_x, start_y - leg],
            [start_x + leg, start_y], 
        ]
    );

module top_triangle (depth, leg, start_x, start_y)
    color("black")
    linear_extrude(depth)
    polygon(
        points=[
            [start_x, start_y],
            [start_x, start_y + leg], 
            [start_x + leg, start_y],
        ]
        
    );

depth = 3.6;
leg = 9.19;
top_width = 14;
vert_trap_width = 16.686;
text_block_width = 2*(leg)+vert_trap_width;
text_block_length = 6*(leg)+3*(top_width)+20.098;
bot_trap_x = leg+top_width;
top_block_width = 12+leg;
top_block_length = 2*(leg)+top_width;

text_rectangle (depth, text_block_width, text_block_length, "end"); // Main block with text
vert_trapezoid (depth, leg, leg, vert_trap_width, text_block_length, 0); // Right end trapezoid
horiz_trapezoid (depth, leg, -leg, top_width, bot_trap_x, -text_block_width); // Bottom trapezoid
block_rectangle (depth, top_block_width, top_block_length, 0, 0); // Added top block to left
top_triangle (depth, leg, top_block_length, 0);
    """

    class_scad_code = f"""
the_matrix = {the_matrix};
export_scale = 1; //USER INPUT
diameter = 1.6;
radius = diameter / 2;
braille_height = 0.6; //USER INPUT
fillet_radius = .4;
spacing = 2.54;
distance = 6.2; // horizontal braille cell spacing
// define braille starting position
letfc = 2; // left edge to first column of braille
line_margin = 1; //USER INPUT
// define plate size
plate_height = 0; //USER INPUT
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
        color("white")
        translate([(leg+top_width)/2, distance * index + leg/2, depth]) {{
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
module horiz_trapezoid (depth, leg_x, leg_y, top_width, left_bottom_x, left_bottom_y) {{
color("black")
linear_extrude(depth)
polygon(
    points=[
        [left_bottom_x, left_bottom_y],  // Bottom left corner
        [left_bottom_x + leg_x, left_bottom_y + leg_y], // Top left corner
        [left_bottom_x + leg_x + top_width, left_bottom_y + leg_y], // Top right corner
        [left_bottom_x + top_width + 2*(leg_x), left_bottom_y]   // Bottom right corner
    ]
);
}}
module vert_trapezoid (depth, leg_x, leg_y, top_width, left_bottom_x, left_bottom_y) {{
    color("black")
    linear_extrude(depth)
    polygon(
        points=[
            [left_bottom_x, left_bottom_y],  // Bottom left corner
            [left_bottom_x + leg_x, left_bottom_y - leg_y], // Top left corner
            [left_bottom_x + leg_x, left_bottom_y - leg_y - top_width], // Top right corner
            [left_bottom_x, left_bottom_y - (top_width + 2*(leg_x))]   // Bottom right corner
        ]
    );
}}
module text_rectangle (depth, block_width, block_length, text) {{
    plate = [block_length, block_width, depth]; // Block
    translate([0, -block_width, 0])
    color("black")
    cube(plate);
    color("white")
    linear_extrude(3*depth/2)
    translate([leg+(top_width/2),-1*leg,0])
    text( text, size = 6, halign = "center");
}}
module block_rectangle (depth, block_width, block_length, start_x, start_y) {{
    plate = [block_length, block_width, depth]; // Block
    translate([start_x, start_y, 0])
    color("black")
    cube(plate);
}}
module indent_rectangle (depth, leg, width_down, block_width, block_length, start_x, start_y) {{
    plate1 = [block_length, block_width, depth]; // Block
    plate2 = [69, 22, depth / 2];
    difference() {{
        translate([start_x - (leg + leg + top_width), start_y, 0])
        color("black")
        cube(plate1);
        translate([0.2, 0.2, 0.2])
        translate([start_x+leg/2, -width_down-leg/4, depth/2])
        color("white")
        cube(plate2);
     }}
}}
module bot_triangle (depth, leg, start_x, start_y)
    color("black")
    linear_extrude(depth)
    polygon(
        points=[
            [start_x, start_y],
            [start_x, start_y - leg],
            [start_x + leg, start_y],
        ]
    );
module top_triangle (depth, leg, start_x, start_y)
    color("black")
    linear_extrude(depth)
    polygon(
        points=[
            [start_x, start_y],
            [start_x + leg, start_y],
            [start_x + leg, start_y + leg],
        ]
 );
module partial_trapezoid (depth, leg_x, leg_y, top_width, left_bottom_x, left_bottom_y)
    color("black")
    linear_extrude(depth)
    polygon(
        points=[
            [left_bottom_x, left_bottom_y],  // Bottom left corner
            [left_bottom_x + leg_x, left_bottom_y + leg_y], // Top left corner
            [left_bottom_x + leg_x + top_width, left_bottom_y + leg_y], // Top right corner
            [left_bottom_x + leg_x + top_width, left_bottom_y]   // Bottom right corner
        ]
);
depth = 3.6;
leg = 9.19;
top_width = 14;
vert_trap_top_width = 17.939;
text_block_width = 46.319;
text_block_length = leg + top_width + leg;
mid_block_width = vert_trap_top_width + leg;
mid_block_length = leg + top_width;
big_block_width = vert_trap_top_width +(2*leg);
big_block_length = 76.835;
partial_trapezoid(depth, leg, leg, top_width, 0, 0); // Top Left Partial Trapezoid
text_rectangle (depth, text_block_width, text_block_length, "class"); // Block with Text
horiz_trapezoid (depth, leg, -leg, top_width, 0, -text_block_width); // Bottom Left Trapezoid
block_rectangle (depth, mid_block_width, mid_block_length, text_block_length, -mid_block_width); // Mid Block
bot_triangle (depth, leg, text_block_length, -mid_block_width); // Bot Triangle
indent_rectangle (depth, leg, vert_trap_top_width, big_block_width, big_block_length + leg + leg + top_width, text_block_length + top_width + leg,-big_block_width + leg); // Big Block
vert_trapezoid (depth, leg, leg, vert_trap_top_width, text_block_length + top_width + leg + big_block_length, leg);
horiz_trapezoid (depth, leg, -leg, top_width, 3*(leg) + 2*(top_width), -vert_trap_top_width-leg); // Bottom Right Trapezoid
"""

    # write SCAD file
    with open(scad_path, "w", encoding="utf-8") as f:
        if block_type == "say":
            f.write(say_scad_code)
        elif block_type == "action":
            f.write(action_scad_code)
        elif block_type == "end":
            f.write(end_scad_code)
        else:
            f.write(class_scad_code)
    # run OpenSCAD → STL
    openscad_executable = "/Applications/OpenSCAD.app/Contents/MacOS/OpenSCAD"  # or your Windows path
    subprocess.run([
        openscad_executable,
        "-o", stl_path,
        scad_path
    ], check=True)

    print(f"Generated {scad_name} and {stl_name} in {scad_folder}")