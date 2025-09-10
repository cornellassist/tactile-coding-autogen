
    the_matrix = [[[[0, 1, 1], [1, 0, 0]], [[1, 0, 0], [0, 0, 0]], [[1, 0, 1], [1, 1, 1]]]];

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
scale([export_scale, export_scale, export_scale]) {
    rotate([0,0,-90]) {
        for (line = [0:len(the_matrix) - 1]) {
            for (char_index = [0:len(the_matrix[line]) - 1]) {
                current_char = the_matrix[line][char_index];
                braille_points(line, char_index, current_char, top_width, connector_side_length);
            }
        }
    }
}
// braille_str transforms each braille character into its position on the plate
module braille_points(line, index, bitmap, top_width, connector_side_length) {
    plate_length = (distance * len(the_matrix[line])) + letfc * 2 - diameter;
    union() {
        color([19/255,56/255,190/255]) { //preview color, blue
            cube([plate_depth * (line+1), plate_length, plate_height]); //rectangular prism backing the braille
        }
        translate([line_margin + plate_depth * line + top_width + 2, distance * index + letfc + connector_side_length, depth]) {
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
module block_trapezoid (depth, leg_x, leg_y, top_width, left_bottom_x, left_bottom_y) {
color("gray")
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
module block_rectangle (depth, leg, top_width, block_width, text) {
plate = [3*(top_width) + 4*(leg), block_width, depth]; // Block
translate([0, -block_width, 0])
color("gray")
cube(plate);
color("white")
linear_extrude(3*depth/2)
translate([(3*(top_width) + 4*(leg))/2, -2*block_width/3, 0])
text( text, size = 6, halign = "center");
}
module connector_trapezoid (depth, leg, top_width, block_width) {
color("gray")
linear_extrude(depth / 2)
polygon(
    points=[
        [3*(top_width) + 4*(leg), -(2*block_width)/3],  // Top left corner
        [3*(top_width) + 4*(leg), -(block_width)/3], // Top right corner
        [3*(top_width) + 4*(leg) + 6.004154, -((block_width)/3) + 3.4665], // Bottom right corner
        [3*(top_width) + 4*(leg) + 6.004154, -((2*block_width)/3) - 3.4665]   // Bottom left corner
    ]
);
}
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
module block_connector (depth, leg, top_width, width, height, start_x) {
difference() {
    plate = [width + leg, height + 2*(leg), depth];
    translate([3*(top_width) + 4*(leg) + 21.24, -height-leg, 0])
    color("gray")
    cube(plate);
    translate([0.02, 0.02, -0.02])
    color("gray")
    top_triangle(depth *2, leg, start_x, leg);
    color("gray")
    translate([0.02, -0.02, -0.02])
    bot_triangle(depth *2, leg, start_x, -height-leg);
    translate([-0.02, 0.02, -0.02])
    color("gray")
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
}
}
block_trapezoid(depth, leg, leg, top_width, 0, 0); // Top Left Trapezoid
block_trapezoid(depth, leg, leg, top_width, 2*(top_width) + 2*(leg), 0); // Top Right Trapezoid
block_rectangle(depth, leg, top_width, block_width, "say"); // Rectangle Block
block_trapezoid(depth, leg, -leg, top_width, 0, -block_width); // Bottom Left Trapezoid
block_trapezoid(depth, leg, -leg, top_width, 2*(top_width)+ 2*(leg), -block_width); // Bottom Right Trapezoid
block_trapezoid(depth, leg, leg, top_width, top_width + leg, -block_width-leg); // Top Half Hexagon
block_trapezoid(depth, leg, -leg, top_width, top_width + leg, -block_width-leg); // Bottom Half Hexagon
connector_trapezoid(depth / 2, leg, top_width, block_width); // Connector Trapezoid
block_connector(depth, leg, top_width, connector_side_length, connector_trapezoid_width, connector_start_x);
    