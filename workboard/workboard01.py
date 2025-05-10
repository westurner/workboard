#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
# workboard01.py
A simple laptop stand model with inset circles for detachable magnetic risers.


## Design a CAD model:

- dimensions: fit under a 15.6" laptop
- materials: wood and/or metal
- feature: inset circles for detachable magnetic laptop risers
- output: build123d procedural CAD model in Python


### CAD Model Notes
- Dimensions are in `mm`

### References:
- https://build123d.readthedocs.io/en/latest/introductory_examples.html

"""
# SPDX-License-Identifier:

import os

# Import necessary modules from build123d
from build123d import (
    Axis,
    Bezier,
    Box,
    Circle,
    Compound,
    Cylinder,
    Line,
    Locations,
    Mode,
    Part,
    Rectangle,
    Vector,
    chamfer,
    export_gltf,
    export_step,
    export_stl,
    fillet,
)
from build123d.build_part import BuildPart
from build123d.build_sketch import BuildSketch
from build123d.geometry import Color, Vector

# Define dimensions for the CAD model
laptop_length = 15.6  # inches
laptop_width = 10.0  # approximate width in inches
laptop_height = 0.8  # approximate height in inches

# Convert dimensions to millimeters (1 inch = 25.4 mm)
laptop_length_mm = laptop_length * 25.4
laptop_width_mm = laptop_width * 25.4
laptop_height_mm = laptop_height * 25.4

# Define the base dimensions for the stand
workboard_length = laptop_length_mm
workboard_width = laptop_width_mm
workboard_height = 25.4 * (5 / 8)  # height of the stand in mm

# Define the inset circle dimensions
circle_diameter = 30  # diameter of the inset circle in mm
circle_depth = 20  # depth of the inset circle in mm

feet_height = 25.4  # height of the feet in mm

circle_positions = [
    # (workboard_length * 0.25, workboard_width * 0.25),
    # (workboard_length * 0.75, workboard_width * 0.25),
    (
        workboard_length * 0.25,
        workboard_width * 0.65 - workboard_width,
        0 #-1 * circle_depth,
    ),
    (
        workboard_length * -0.25,
        workboard_width * 0.65 - workboard_width,
        -1 * circle_depth,
    ),
]

show_feet_as = "attached"
#show_feet_as = 'detached'


class Colors:
    GrayAlpha100 = Color(0.7, 0.7, 0.7, 1.0)
    GrayAlpha08 = Color(0.7, 0.7, 0.7, 0.8)
    SilverGrayAlpha08 = Color(0.5, 0.5, 0.5, 0.8)
    DarkGrayAlpha08 = Color(0.3, 0.3, 0.3, 0.8)



# def svg_path_to_build123d(svg_path: str):
#     """
#     Translates an SVG path string to build123d Python code.

#     Args:
#         svg_path (str): The SVG path string.

#     Returns:
#         BuildSketch: A build123d sketch object representing the path.
#     """
#     with BuildSketch() as sketch:
#         for svg_path_line in svg_path.splitlines():
#             commands = svg_path_line.split()
#             i = 0
#             while i < len(commands):
#                 command = commands[i]
#                 if command == 'm':  # Move to
#                     x, y = map(float, commands[i + 1].split(','))
#                     #sketch.move_to(Vector(x, y))
#                     sketch.current_position = Vector(x,y)
#                     i += 2
#                 elif command == 'c':  # Cubic Bezier curve
#                     control1 = tuple(map(float, commands[i + 1].split(',')))
#                     control2 = tuple(map(float, commands[i + 2].split(',')))
#                     end_point = tuple(map(float, commands[i + 3].split(',')))
#                     Bezier(sketch.current_position, Vector(*control1), Vector(*control2), Vector(*end_point))
#                     i += 4
#                 elif command == 'V':  # Vertical line
#                     y = float(commands[i + 1])
#                     Line(sketch.current_position, Vector(sketch.current_position.X, y))
#                     i += 2
#                 elif command == 'H':  # Horizontal line
#                     x = float(commands[i + 1])
#                     Line(sketch.current_position, Vector(x, sketch.current_position.Y))
#                     i += 2
#                 elif command == 'z':  # Close path
#                     # sketch.close()  # TODO
#                     i += 1
#                 else:
#                     i += 1  # Skip unrecognized commands
#     return sketch


def build_workboard():
    with BuildPart() as base3d:
        # with BuildSketch() as sketch1:
        #     # Create a rectangle for the base of the stand
        #     Rectangle(workboard_length, workboard_width)
        #     # Create inset circles for detachable magnetic laptop risers
        #     for x, y in circle_positions:
        #         Circle(radius=circle_diameter / 2)

        base3d.color = Colors.SilverGrayAlpha08

        with BuildPart() as workboard:
            # workboard.color = Colors.SilverGrayAlpha08  # TODO: doesn't seem to work?
            board = Part() + Box(
                length=workboard_length, width=workboard_width, height=workboard_height
            )
            print(f"{board.edges()=}")
            fillet(board.edges(), radius=25.4 * 0.25)  # Fillet the edges with a radius of 10 mm

            with Locations(*circle_positions):
                # Create inset circles for detachable magnetic laptop risers
                inset = Cylinder(radius=circle_diameter / 2, height=feet_height, mode=Mode.SUBTRACT)
                #inset.chamfer(1, None, (inset.faces()>>Axis.Z)[0].edges())


            # Create a line with an inward curve at 0.8 / 1.0 along the right side of the board
            # todo_curvy_edge()


        with BuildPart() as magnetic_discs:
            # Create magnetic discs for the insets
            with Locations(*circle_positions):
                cylinder = Cylinder(
                    radius=((circle_diameter - 2) / 2),
                    height=0.2,
                )

        with BuildPart() as feet:
            # Create magnetic feet
            feet.color = Colors.DarkGrayAlpha08
            if show_feet_as == "attached":
                with Locations(*circle_positions):
                    Cylinder(radius=((circle_diameter - 2) / 2), height=feet_height)

        # # [fillet(cylinder.edges(), radius=0.1) for cylinder in cylinders]  # Fillet the edges of the cylinders
        # # fillet(cylinders.edges(), radius=10)  # Fillet the edges of the cylinders


        # Example usage
        svg_path = """
        m 83.73,35.95
        c 7.82,0 671.2,0 671.2,0 8.08,0 17.68,6.45 16.28,17.95 -3,24.57 -8.2,72.15 -11.29,128.95 -2.15,39.48 13.62,142.27 13.62,190.57
        V 1024.54
        H 69.77
        c 0,0 0,-966.8 0,-976.36 0,-9.55 6.14,-12.24 13.96,-12.24
        z
        """
        # sketch = svg_path_to_build123d(svg_path)


    return {
        "parts": {
            "base3d": base3d,
            "workboard": workboard,
            "discs": magnetic_discs,
            "feet": feet,
        },
        "sketches": {

        }
    }


def todo_curvy_edge(board):
    # Create a curvy edge line
    line = board.edges()[0].to_wire()
    # Create a curvy edge line
    curvy_edge = line.curve().to_spline()
    # Replace the edge with the curvy edge line
    board.replace_edge(board.edges()[0], curvy_edge)



data = build_workboard()
do_export_files = False
if do_export_files:
    # name_prefix = "workboard01"
    name_prefix = __file__.split(".")[0]  # Use the script name as the prefix
    for name, base in data["parts"]:
        # Export the model
        export_step(base, f"{name_prefix}_{name}.step")

        # Export the model as an STL file
        export_stl(base, f"{name_prefix}_{name}.stl")

        # Export the model as an STL file
        export_stl(base, f"{name_prefix}_{name}.txt.stl", ascii_format=True)

        # Export the model as an STL file
        export_gltf(base, f"{name_prefix}_{name}.gltf")

def running_in_vscode():
    return "VSCODE_IPC_HOOK_CLI" in os.environ

if running_in_vscode():
    # ocp_vscode is used to visualize the model in VSCode
    # Install the "OCP CAD Viewer" extension in VSCode to view the model
    from ocp_vscode import show

    # Ensure ocp_vscode is installed to visualize the model in VSCode
    # Install ocp_vscode via pip if not already installed:
    # pip install ocp-vscode
    # Show the model in the OCP VSCode viewer
    try:
        show(data["parts"]["base3d"], "Workboard 3D Model")
    except RuntimeError as exc:
        print(exc)
        print("""In vscode: Ctrl-Shift-P "OCP CAD Viewer: Open viewer (Ctrl+K V)""")
        raise
    # This code creates a simple laptop stand model with inset circles for detachable magnetic risers.
    # The model is exported in STEP and STL formats for further use or 3D printing.
