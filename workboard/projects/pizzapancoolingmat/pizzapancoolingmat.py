"""
Passive Laptop Cooling Mat Components using build123d

This module defines parametric components for a passive laptop cooling mat:
- PizzaPanComponent: 13" aluminum pizza pan
- MagneticLaptopRiserComponent: silicone magnetic laptop riser/feet
- LaptopComponent: simplified 15.6" laptop
- PizzaPanCoolingMatAssembly: assembly of the above
"""
import os
from typing import Any, Dict

from build123d import Part, Cylinder, Box, Location
from build123d.topology import Compound  #, Edge, Face, ShapeList, Solid, Sketch

from workboard.projects.pizzapancoolingmat.schemas import DEFAULTS


class PizzaPanComponent:
    """
    Represents a 13" aluminum pizza pan.
    Args:
        props (dict): Properties for the pan (diameter, thickness).
    """
    def __init__(self, props: Dict[str, Any]):
        defaults = self.defaultProps()
        self.props = {**defaults, **props}

    @staticmethod
    def defaultProps():
        return DEFAULTS["default0"]["pan"]

    def render(self) -> Compound:
        """
        Render the pizza pan geometry.
        Returns:
            Part: build123d Part representing the pan.
        """
        diameter = self.props["diameter"]
        thickness = self.props["thickness"]
        rim_height = self.props["rim_height"]
        # Main disk
        disk = Cylinder(diameter / 2, thickness)
        # Rim (optional)
        rim = Cylinder(diameter / 2, rim_height)
        rim = rim - Cylinder((diameter / 2) - 10, rim_height)
        rim = rim.translate((0, 0, thickness))
        pan = disk + rim
        # Ensure the bottom of the pan is at Z=0 (disk and rim both start at Z=0)
        # If the bounding box min.Z is not 0, translate pan down
        min_z = pan.bounding_box().min.Z
        if abs(min_z) > 1e-6:
            pan = pan.translate((0, 0, -min_z))
        return pan


class MagneticLaptopRiserSquareComponent:
    """
    Represents a silicone magnetic laptop riser/foot.
    Args:
        props (dict): Properties for the riser (length, width, height).
    """
    def __init__(self, props: Dict[str, Any]):
        defaults = self.defaultProps()
        self.props = {**defaults, **props}

    @staticmethod
    def defaultProps():
        return DEFAULTS["default0"]["riser"]

    def render(self) -> Part:
        """
        Render the riser geometry.
        Returns:
            Part: build123d Part representing the riser.
        """
        length = self.props["length"]
        width = self.props["width"]
        height = self.props["height"]
        return Box(length, width, height)


class LaptopComponent:
    """
    Represents a simplified 15.6" laptop.
    Args:
        props (dict): Properties for the laptop (length, width, thickness).
    """
    def __init__(self, props: dict[str, Any], children=None):
        defaults = self.defaultProps()
        self.props = {**defaults, **props}
        self.children = children

    @staticmethod
    def defaultProps():
        return DEFAULTS["default0"]["laptop"]

    def render(self) -> Part:
        """
        Render the laptop geometry.
        Returns:
            Part: build123d Part representing the laptop.
        """
        length = self.props["length"]
        width = self.props["width"]
        thickness = self.props["thickness"]
        return Box(length, width, thickness)


class PizzaPanCoolingMatAssembly:
    """
    Assembly of 2 pizza pans, 4 risers, and 1 laptop.
    Args:
        props: dict of all component props, e.g. {"pan": {...}, "riser": {...}, "laptop": {...}}
        children: optional, for future extensibility
    """
    def __init__(self, props: dict[str, Any], children=None):
        defaults = self.defaultProps()
        self.props = {**defaults, **props}
        self.children = children

    @staticmethod
    def defaultProps():
        return DEFAULTS["default0"]

    def render(self) -> Compound:
        """
        Render the full cooling mat assembly.
        Returns:
            Assembly: build123d Assembly of all components.
        """
        props = self.props

        # --- Z height constants and offsets ---
        pan_thickness = props["pan"]["thickness"]
        pan_rim_height = props["pan"]["rim_height"]
        riser_height = props["riser"]["height"]
        riser_z_offset = 15  # Distance from base to bottom of riser (could be a prop)
        # The top of the riser is at riser_z_offset + riser_height
        # The bottom of pan2 should be at the top of the risers
        # Render a riser to get its bounding box
        riser_geom = MagneticLaptopRiserSquareComponent(props["riser"]).render()
        riser_top_z = riser_z_offset + (riser_geom.bounding_box().max.Z - riser_geom.bounding_box().min.Z)
        # Render a pan to get its bounding box
        pan_geom = PizzaPanComponent(props["pan"]).render()
        pan1 = pan_geom
        # Place risers so their bottom is at the top of pan1
        pan1_top_z = pan1.bounding_box().max.Z
        riser_geom = MagneticLaptopRiserSquareComponent(props["riser"]).render()
        riser_height = props["riser"]["height"]
        riser_z_offset = pan1_top_z  # Place riser bottom at pan1 top
        # Render a pan to get its bounding box
        pan_geom = PizzaPanComponent(props["pan"]).render()
        riser_top_z = riser_z_offset + (riser_geom.bounding_box().max.Z - riser_geom.bounding_box().min.Z)
        pan2_z = riser_top_z - pan_geom.bounding_box().min.Z
        pan2 = pan_geom.translate((0, 0, pan2_z))
        # Place laptop so its bottom is at the top of pan2
        laptop_geom = LaptopComponent(props["laptop"]).render()
        laptop_z = pan2.bounding_box().max.Z - laptop_geom.bounding_box().min.Z
        risers = []
        for i in range(4):
            x = (-100 if i < 2 else 100)
            y = (-80 if i % 2 == 0 else 80)
            riser_geom = MagneticLaptopRiserSquareComponent(props["riser"]).render()
            riser = riser_geom.translate((x, y, riser_z_offset + riser_height / 2))
            risers.append(riser)
        laptop = laptop_geom.translate((0, 0, laptop_z))

        asm = Compound()
        parts = []
        parts.append(pan1) #, name="pan1")
        parts.append(pan2) #, name="pan2"
        for idx, riser in enumerate(risers):
            parts.append(riser) #, name=f"riser{idx+1}")
        parts.append(laptop) #, name="laptop")
        asm.children = parts
        return asm


def running_in_vscode():
    return "VSCODE_IPC_HOOK_CLI" in os.environ

def main():
    props = DEFAULTS["default0"]
    assert "pan" in props
    assert "riser" in props
    assert "laptop" in props
    asm = PizzaPanCoolingMatAssembly(
        props
    ).render()
    if running_in_vscode():
        from ocp_vscode import show
        show(asm)
    else:
        print(asm)

if __name__ == "__main__":
    main()

