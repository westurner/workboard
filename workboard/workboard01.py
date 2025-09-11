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


import types

class Conf(types.SimpleNamespace):
    pass


import unittest
from dataclasses import dataclass, field
from typing import Dict, Any
from types import SimpleNamespace # Or your custom ArbitraryAttributes class

@dataclass
class Component:
    id: int|str
    name: str
    props: Dict[str, Any] = field(default_factory=dict, init=True, repr=True, compare=True)
    # ^ We use a private name and exclude from init, repr, compare because
    # we'll handle it specially. init=True means it's passed in __init__,
    # but we'll override it.

    _props_proxy: SimpleNamespace = field(init=False, repr=False, compare=False)

    def __post_init__(self):
        # Create a SimpleNamespace to proxy arbitrary attributes
        # We ensure props is a dict before passing it
        if not isinstance(self.props, dict):
            raise TypeError("'props' must be a dictionary")
        self._props_proxy = SimpleNamespace(**self.props)

    def __getattr__(self, name: str) -> Any:
        # First, try to get it from the structured dataclass fields
        # This will be handled by dataclasses' default __getattr__ for declared fields
        # If it falls through here, it's not a declared field.
        try:
            # Try to get it from the dynamic attributes proxy
            return getattr(self._props_proxy, name)
        except AttributeError:
            # If not found in dynamic attributes either, raise the standard AttributeError
            raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{name}'")

    def __setattr__(self, name: str, value: Any) -> None:
        # If it's a declared dataclass field, let dataclasses handle it normally
        # This check is important to prevent infinite recursion and ensure dataclass fields work
        if name in self.__dataclass_fields__:
            super().__setattr__(name, value)
        else:
            # Otherwise, set it on the dynamic attributes proxy
            setattr(self._props_proxy, name, value)
            # And update the underlying dictionary for serialization/persistence
            self.props[name] = value

    def __delattr__(self, name: str) -> None:
        if name in self.__dataclass_fields__:
            super().__delattr__(name)
        else:
            try:
                delattr(self._props_proxy, name)
                del self.props[name]
            except AttributeError:
                raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{name}'")


def test_thing() -> bool:
    # Example Usage
    obj = Component(id=1, name="Bob", props={'location': 'Mars', 'status': 'active'})

    assert obj.id == 1        # Access structured field
    assert obj.name == "Bob"      # Access structured field
    assert obj.location == "Mars"  # Access arbitrary attribute via dot notation
    assert obj.status == "active"    # Access arbitrary attribute via dot notation

    obj.planet = "Jupiter" # Set new arbitrary attribute
    obj.zip_code = 12345   # Set another new arbitrary attribute
    assert obj.planet == "Jupiter"
    assert obj.zip_code == 12345

    assert obj.id == 1
    assert obj.name == "Bob"
    assert obj.props['location'] == "Mars"
    assert obj.props['planet'] == "Jupiter"
    assert obj.props['zip_code'] == 12345

    assert repr(obj) == "Component(id=1, name='Bob', props={'location': 'Mars', 'status': 'active', 'planet': 'Jupiter', 'zip_code': 12345})"

    # You can still access the underlying dict if needed
    assert (obj.props ==
        {'location': 'Mars', 'status': 'active', 'planet': 'Jupiter', 'zip_code': 12345})

    # del obj.location
    # assert "location" not in obj.props
    # test = unittest.TestCase()
    # with test.assertRaises(AttributeError):
    #     print(obj.location)


    return True


class Workboard(Component):

    def init(self):
        #obj = types.SimpleNamespace()
        #obj = Component(id=1, name="workboard01")

        # Define dimensions for the CAD model
        self.laptop_length = 15.6  # inches
        self.laptop_width = 10.0  # approximate width in inches
        self.laptop_height = 0.8  # approximate height in inches

        # Convert dimensions to millimeters (1 inch = 25.4 mm)
        self.laptop_length_mm = self.laptop_length * 25.4
        self.laptop_width_mm = self.laptop_width * 25.4
        self.laptop_height_mm = self.laptop_height * 25.4

        # Define the base dimensions for the stand
        self.workboard_length = self.laptop_length_mm
        self.workboard_width = self.laptop_width_mm
        self.workboard_height = 25.4 * (5 / 8)  # height of the stand in mm
        self.workboard_color = Colors.WoodColor3_a100
        self.workboard_material = None

        # Define the inset circle dimensions
        self.circle_diameter = 30  # diameter of the inset circle in mm
        self.circle_depth = 20  # depth of the inset circle in mm

        self.workboard_magnetic_disc_diameter = self.circle_diameter - 2
        self.workboard_magnetic_disc_height = 1.0
        self.workboard_magnetic_disc_color = Colors.MagnetBlack_a80
        self.workboard_magnetic_disc_material = None

        self.feet_height = 20  # height of the feet in mm
        self.feet_diameter = 25.4
        self.feet_color = Colors.DarkGray_a100
        self.feet_material = None

        self.feet_magnetic_disc_diameter = self.feet_diameter - 2  # TODO
        # obj.feet_magnetic_disc_diameter =  ((obj.circle_diameter / 2) - 1),
        self.feet_magnetic_disc_height = 1.0
        self.feet_magnetic_disc_color = Colors.MagnetBlack_a80
        self.feet_magnetic_disc_material = None

        self.circle_positions = [
            # (obj.workboard_length * 0.25, obj.workboard_width * 0.25),
            # (obj.workboard_length * 0.75, obj.workboard_width * 0.25),
            (
                self.workboard_length * 0.25,
                self.workboard_width * 0.65 - self.workboard_width,
                self.feet_height / 2,  # 0  # -1 * circle_depth,
            ),
            (
                self.workboard_length * -0.25,
                self.workboard_width * 0.65 - self.workboard_width,
                self.feet_height / 2,  # -1 * circle_depth,
            ),
        ]

        self.show_feet_as = "attached"
        # obj.show_feet_as = 'detached'


    def render(self):
        cfg = self
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
            with Locations((0, 0, cfg.feet_height)):
                board = Box(
                    length=cfg.workboard_length,
                    width=cfg.workboard_width,
                    height=cfg.workboard_height,
                )

            with Locations(*cfg.circle_positions):
                # Create inset circles for detachable magnetic laptop risers
                inset = Cylinder(
                    radius=cfg.circle_diameter / 2,
                    height=cfg.feet_height,
                    mode=Mode.SUBTRACT,
                )
                # TODO: chamfer the edges
                #inset.chamfer(1, None, (inset.faces() >> Axis.Z)[0].edges())
                

            # with Locations(
            #     [
            #         (x[0], x[1], cfg.feet_height + (cfg.workboard_magnetic_disc_height / 2))
            #         for x in cfg.circle_positions
            #     ]
            # ):
            #     Cylinder(
            #         radius=(cfg.workboard_magnetic_disc_diameter / 2) + 1,
            #         height=cfg.workboard_magnetic_disc_height,
            #         mode=Mode.SUBTRACT,
            #     )

            # print(f"{board.edges()=}")
            fillet(
                board.edges(), radius=25.4 * 0.25
            )  # Fillet the edges with a radius of 10 mm

            # Create a line with an inward curve at 0.8 / 1.0 along the right side of the board
            # self.todo_curvy_edge(board)

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
                workboard_magnetic_discs.part.material = (
                    cfg.workboard_magnetic_disc_material
                )

            workboard.part.label = "workboard"
            workboard.part.color = cfg.workboard_color
            workboard.part.material = cfg.workboard_material

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
                feet_magnetic_discs.part.material = cfg.feet_magnetic_disc_material

            feet.part.label = "feet"
            feet.part.color = cfg.feet_color
            feet.part.material = cfg.feet_material

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


    @staticmethod
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


def main_test():
    print("INFO: main_test() starting...")
    assert test_thing()
    print("INFO: main_test() done.")


def running_in_vscode() -> bool:
    return "VSCODE_IPC_HOOK_CLI" in os.environ


def main() -> int:
    obj = Workboard(id=1, name="workboard01")
    obj.init()
    data = obj.render()

    do_export_files = True
    if do_export_files:
        data["export_part_filenames"] = export_files(
            filenameprefixsuffix="part", partsiterable=data["parts"].items()
        )
        data["export_assembly_filenames"] = export_files(
            filenameprefixsuffix="assembly", partsiterable=data["assemblies"].items()
        )

    print("DEBUG: pprint(data)=")
    pprint.pprint(data, sort_dicts=False)

    if running_in_vscode():
        # ocp_vscode is used to visualize the model in VSCode
        # Install the "OCP CAD Viewer" extension in VSCode to view the model
        from ocp_vscode import show_all  # , show

        # Ensure ocp_vscode is installed to visualize the model in VSCode
        # Install ocp_vscode via pip if not already installed:
        # $ pip install ocp-vscode

        main_test()

        # Show the model in the OCP VSCode viewer
        try:
            show_all(data["assemblies"])
            # show(data["parts"]["base3d"], "Workboard 3D Model")
        except RuntimeError as exc:
            print(exc)
            print("""In vscode: Ctrl-Shift-P "OCP CAD Viewer: Open viewer (Ctrl+K V)""")
            raise

    return 0


if __name__ == "__main__":
    main()