
the_matrix = [[[[1, 0, 0], [0, 0, 0]], [[1, 0, 0], [1, 0, 0]], [[0, 0, 0], [0, 1, 1]], [[1, 0, 1], [1, 1, 0]]]];
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

    scale([export_scale, export_scale, export_scale]) {
        rotate([0,0,-90]) {
            for (line = [0:len(the_matrix) - 1]) {
                for (char_index = [0:len(the_matrix[line]) - 1]) {
                    current_char = the_matrix[line][char_index];
                    braille_points(line, char_index, current_char);
                }
            }
        }
    }

    // braille_str transforms each braille character into its position on the plate
    module braille_points(line, index, bitmap) {
        plate_length = (distance * len(the_matrix[line])) + letfc * 2 - diameter;
        
        union() {
            color([19/255,56/255,190/255]) { //preview color, blue 
                cube([plate_depth * (line+1), plate_length, plate_height]); //rectangular prism backing the braille
            }
            color("white")
            translate([(leg+top_width)/2, distance * index + leg/2, depth]) {
                for (col = [0:1]) {
                    for (row = [0:2]) {
                        if (bitmap[col][row] == 1) {
                            translate([spacing * (row) + radius, spacing * (col) + radius, 0]) {
                                rotate_extrude($fn = 20) // revolve each braille dot
                                    polygon(points);
                            }
                        }
                    }
                }
            }
        }
    }
module horiz_trapezoid (depth, leg_x, leg_y, top_width, left_bottom_x, left_bottom_y) {
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
}
module vert_trapezoid (depth, leg_x, leg_y, top_width, left_bottom_x, left_bottom_y) {
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
}
module text_rectangle (depth, block_width, block_length, text) {
    plate = [block_length, block_width, depth]; // Block
    translate([0, -block_width, 0])
    color("black")
    cube(plate);
    color("white")
    linear_extrude(3*depth/2)
    translate([leg+(top_width/2),-1*leg,0])
    text( text, size = 6, halign = "center");
    
}
module block_rectangle (depth, block_width, block_length, start_x, start_y) {
    plate = [block_length, block_width, depth]; // Block
    translate([start_x, start_y, 0])
    color("black")
    cube(plate);
}
module indent_rectangle (depth, leg, width_down, block_width, block_length, start_x, start_y) {
    plate1 = [block_length, block_width, depth]; // Block
    plate2 = [69, 22, depth / 2];
    
    difference() {
        translate([start_x, start_y, 0])
        color("black")
        cube(plate1);
        
        translate([0.2, 0.2, 0.2])
        translate([start_x+leg/2, -width_down-leg/4, depth/2])
        color("white")
        cube(plate2);  
     }
    
}
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
    