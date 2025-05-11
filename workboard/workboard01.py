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
import pprint

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


class Colors:
    Gray_a0 = Color(0.7, 0.7, 0.7, 0)
    Gray_a80 = Color(0.7, 0.7, 0.7, 0.8)
    Gray_a100 = Color(0.7, 0.7, 0.7, 1.0)
    SilverGray_a0 = Color(0.5, 0.5, 0.5, 0)
    SilverGray_a80 = Color(0.5, 0.5, 0.5, 0.8)
    SilverGray_a100 = Color(0.5, 0.5, 0.5, 1.0)
    DarkGray_a0 = Color(0.3, 0.3, 0.3, 0)
    DarkGray_a80 = Color(0.3, 0.3, 0.3, 0.8)
    DarkGray_a100 = Color(0.3, 0.3, 0.3, 1.0)
    BrightRed_a80 = Color(0.8, 0, 0, 0.8)
    MagnetBlack_a0 = Color(0.1, 0.1, 0.1, 0)
    MagnetBlack_a80 = Color(0.1, 0.1, 0.1, 0.8)
    MagnetBlack_a100 = Color(0.1, 0.1, 0.1, 1)

    WoodColor1_a100 = Color(225 / 256, 187 / 256, 140 / 256, 1)
    WoodColor2_a100 = Color(0xA8 / 0xFF, 0x78 / 0xFF, 0x3C / 0xFF, 1)
    WoodColor3_a100 = Color(0x66 / 0xFF, 0x49 / 0xFF, 0x25 / 0xFF, 1)


class Conf:
    pass


def build_config():
    cfg = Conf()

    # Define dimensions for the CAD model
    cfg.laptop_length = 15.6  # inches
    cfg.laptop_width = 10.0  # approximate width in inches
    cfg.laptop_height = 0.8  # approximate height in inches

    # Convert dimensions to millimeters (1 inch = 25.4 mm)
    cfg.laptop_length_mm = cfg.laptop_length * 25.4
    cfg.laptop_width_mm = cfg.laptop_width * 25.4
    cfg.laptop_height_mm = cfg.laptop_height * 25.4

    # Define the base dimensions for the stand
    cfg.workboard_length = cfg.laptop_length_mm
    cfg.workboard_width = cfg.laptop_width_mm
    cfg.workboard_height = 25.4 * (5 / 8)  # height of the stand in mm
    cfg.workboard_color = Colors.WoodColor3_a100

    # Define the inset circle dimensions
    cfg.circle_diameter = 30  # diameter of the inset circle in mm
    cfg.circle_depth = 20  # depth of the inset circle in mm

    cfg.workboard_magnetic_disc_diameter = cfg.circle_diameter - 2
    cfg.workboard_magnetic_disc_height = 1.0
    cfg.workboard_magnetic_disc_color = Colors.MagnetBlack_a80

    cfg.feet_height = 25.4  # height of the feet in mm
    cfg.feet_diameter = 25.4
    cfg.feet_color = Colors.DarkGray_a100

    cfg.feet_magnetic_disc_diameter = cfg.feet_diameter - 2  # TODO
    # cfg.feet_magnetic_disc_diameter =  ((cfg.circle_diameter / 2) - 1),
    cfg.feet_magnetic_disc_height = 1.0
    cfg.feet_magnetic_disc_color = Colors.MagnetBlack_a80

    cfg.circle_positions = [
        # (cfg.workboard_length * 0.25, cfg.workboard_width * 0.25),
        # (cfg.workboard_length * 0.75, cfg.workboard_width * 0.25),
        (
            cfg.workboard_length * 0.25,
            cfg.workboard_width * 0.65 - cfg.workboard_width,
            cfg.feet_height / 2,  # 0  # -1 * circle_depth,
        ),
        (
            cfg.workboard_length * -0.25,
            cfg.workboard_width * 0.65 - cfg.workboard_width,
            cfg.feet_height / 2,  # -1 * circle_depth,
        ),
    ]

    cfg.show_feet_as = "attached"
    # cfg.show_feet_as = 'detached'

    return cfg


def build_workboard(cfg):
    if cfg is None:
        raise ValueError("cfg must not be None")

    # with BuildPart() as base3d:
    # with BuildSketch() as sketch1:
    #     # Create a rectangle for the base of the stand
    #     Rectangle(cfg.workboard_length, cfg.workboard_width)
    #     # Create inset circles for detachable magnetic laptop risers
    #     for x, y in circle_positions:
    #         Circle(radius=circle_diameter / 2)

    with BuildPart() as workboard:
        # workboard.color = Colors.SilverGray_a08  # TODO: doesn't seem to work?
        with Locations((0, 0, cfg.feet_height)):
            board = Part() + Box(
                length=cfg.workboard_length,
                width=cfg.workboard_width,
                height=cfg.workboard_height,
            )
            print(f"{board.edges()=}")

        with Locations(*cfg.circle_positions):
            # Create inset circles for detachable magnetic laptop risers
            inset = Cylinder(
                radius=cfg.circle_diameter / 2,
                height=cfg.feet_height,
                mode=Mode.SUBTRACT,
            )
            # inset.chamfer(1, None, (inset.faces()>>Axis.Z)[0].edges())

        with Locations(
            [
                (x[0], x[1], cfg.feet_height + (0 * cfg.feet_magnetic_disc_height / 2))
                for x in cfg.circle_positions
            ]
        ):
            Cylinder(
                radius=(cfg.workboard_magnetic_disc_diameter / 2) + 1,
                height=cfg.workboard_magnetic_disc_height,
                mode=Mode.SUBTRACT,
            )

        print(f"{board.edges()=}")
        fillet(
            board.edges(), radius=25.4 * 0.25
        )  # Fillet the edges with a radius of 10 mm

        # Create a line with an inward curve at 0.8 / 1.0 along the right side of the board
        # todo_curvy_edge()

        with BuildPart() as workboard_magnetic_discs:
            # Create magnetic discs for the insets
            with Locations(
                [
                    (
                        x[0],
                        x[1],
                        cfg.feet_height + (cfg.workboard_magnetic_disc_height / 2),
                    )
                    for x in cfg.circle_positions
                ]
            ):
                Cylinder(
                    radius=cfg.workboard_magnetic_disc_diameter / 2,
                    height=cfg.workboard_magnetic_disc_height,
                )
            workboard_magnetic_discs.part.label = "workboard.magnets"
            workboard_magnetic_discs.part.color = cfg.workboard_magnetic_disc_color

        workboard.part.label = "workboard"
        workboard.part.color = cfg.workboard_color

    with BuildPart() as feet:
        # Create magnetic feet
        if cfg.show_feet_as == "attached":
            with Locations(*cfg.circle_positions):
                foot = Cylinder(radius=(cfg.feet_diameter / 2), height=cfg.feet_height)
                fillet(
                    foot.edges().filter_by_position(
                        Axis.Z, 0, 1, inclusive=(True, False)
                    ),
                    radius=cfg.feet_height / 3,
                )

        with BuildPart() as feet_magnetic_discs:
            # Create magnetic discs for the insets
            with Locations(
                [
                    (x[0], x[1], cfg.feet_height - (cfg.feet_magnetic_disc_height / 2))
                    for x in cfg.circle_positions
                ]
            ):
                Cylinder(
                    radius=cfg.feet_magnetic_disc_diameter / 2,
                    height=cfg.feet_magnetic_disc_height,
                )
            feet_magnetic_discs.part.label = "feet.magnets"
            feet_magnetic_discs.part.color = cfg.feet_magnetic_disc_color

        feet.part.label = "feet"
        feet.part.color = cfg.feet_color

    # Example usage
    todo_svg_path = """
    m 83.73,35.95
    c 7.82,0 671.2,0 671.2,0 8.08,0 17.68,6.45 16.28,17.95 -3,24.57 -8.2,72.15 -11.29,128.95 -2.15,39.48 13.62,142.27 13.62,190.57
    V 1024.54
    H 69.77
    c 0,0 0,-966.8 0,-976.36 0,-9.55 6.14,-12.24 13.96,-12.24
    z
    """
    # sketch = svg_path_to_build123d(svg_path)

    data = {
        "parts": {
            "workboard": workboard,
            "workboard_magnetic_discs": workboard_magnetic_discs,
            "feet_magnetic_discs": feet_magnetic_discs,
            "feet": feet,
        },
        "sketches": {},
        "assemblies": {},
    }

    workboard_assembly = data["assemblies"]["workboard_assembly"] = Compound(
        label="workboard", children=[v.part for v in data["parts"].values() if v]
    )

    print("DEBUG: workboard_assembly.show_topology()=")
    print(workboard_assembly.show_topology())
    return data


def todo_curvy_edge(board):
    # Create a curvy edge line
    line = board.edges()[0].to_wire()
    # Create a curvy edge line
    curvy_edge = line.curve().to_spline()
    # Replace the edge with the curvy edge line
    board.replace_edge(board.edges()[0], curvy_edge)


def export_files(*, filenameprefix=None, filenameprefixsuffix=None, partsiterable):
    exportfilenames = {}

    if filenameprefix is None:
        filename_prefix = __file__.split(".")[0]  # Use the script name as the prefix
    else:
        filename_prefix = filenameprefix

    if filenameprefixsuffix:
        filename_prefix = f"{filename_prefix}__{filenameprefixsuffix}_"

    for name, base in partsiterable:
        if filenameprefixsuffix == "part":
            part = base.part
        else:
            part = base

        exportfilenames[".step"] = f"{filename_prefix}_{name}.step"
        exportfilenames[".stl"] = f"{filename_prefix}_{name}.stl"
        exportfilenames[".txt.stl"] = f"{filename_prefix}_{name}.txt.stl"
        exportfilenames[".gltf"] = f"{filename_prefix}_{name}.gltf"

        # Export the model
        export_step(part, exportfilenames[".step"])

        # Export the model as an STL file
        export_stl(part, exportfilenames[".stl"])

        # Export the model as an STL file
        export_stl(part, exportfilenames[".txt.stl"], ascii_format=True)

        # Export the model as an STL file
        export_gltf(part, exportfilenames[".gltf"])

    return exportfilenames


def running_in_vscode():
    return "VSCODE_IPC_HOOK_CLI" in os.environ


def main():
    cfg = build_config()
    data = build_workboard(cfg)

    do_export_files = True
    if do_export_files:
        data["export_part_filenames"] = export_files(
            filenameprefixsuffix="part", partsiterable=data["parts"].items()
        )
        data["export_assembly_filenames"] = export_files(
            filenameprefixsuffix="assembly", partsiterable=data["assemblies"].items()
        )
    pprint.pprint(data, sort_dicts=False)


    if running_in_vscode():
        # ocp_vscode is used to visualize the model in VSCode
        # Install the "OCP CAD Viewer" extension in VSCode to view the model
        from ocp_vscode import show_all  # , show

        # Ensure ocp_vscode is installed to visualize the model in VSCode
        # Install ocp_vscode via pip if not already installed:
        # $ pip install ocp-vscode

        # Show the model in the OCP VSCode viewer
        try:
            show_all(data["assemblies"])
            # show(data["parts"]["base3d"], "Workboard 3D Model")
        except RuntimeError as exc:
            print(exc)
            print("""In vscode: Ctrl-Shift-P "OCP CAD Viewer: Open viewer (Ctrl+K V)""")
            raise


if __name__ == "__main__":
    main()