"""
Passive Laptop Cooling Mat Components using build123d

This module defines parametric components for a passive laptop cooling mat:
- PizzaPanComponent: 13" aluminum pizza pan
- MagneticLaptopRiserComponent: silicone magnetic laptop riser/feet
- LaptopComponent: simplified 15.6" laptop
- PizzaPanCoolingMatAssembly: assembly of the above

TODO:
- update the dimensions of the laptop
- 
- increase the details on the laptop
- switch from absolute to relative measurement

"""
import os
from typing import Any, Dict

from build123d import Axis, Part, Cylinder, Box, Location
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
        rim = rim.translate((0, 0, thickness-1))
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


GAP_TOLERANCE = 0.0001

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

        pan_thickness = props["pan"]["thickness"]
        #pan_rim_height = props["pan"]["rim_height"]
        riser_height = props["riser"]["height"]
        laptop_thickness = props["laptop"]["thickness"]

        # The top of the riser is at riser_z_offset + riser_height
        # The bottom of pan2 should be at the top of the risers
        # Render a riser to get its bounding box
        magnet_geom = MagneticLaptopRiserSquareComponent(props["riser"]).render()
        
        # Render a pan to get its bounding box
        pan_geom = PizzaPanComponent(props["pan"]).render()
        pan1 = pan_geom
        pan1.label = "Pan 1"


        magnet_geom = MagneticLaptopRiserSquareComponent(props["riser"]).render()

        risers = []
        risers1_z = pan_thickness + GAP_TOLERANCE  # Distance from base to bottom of riser (could be a prop)
        risers1_z = (risers1_z + riser_height / 2)

        for i in range(2):
            x = (-100)
            y = (-80 if i % 2 == 0 else 80)
            riser = magnet_geom.rotate(Axis.Z, 90)
            riser = riser.translate((x, y, risers1_z))
            riser.label = "Magnet (Layer 1)"
            risers.append(riser)

        risers1_top_z = risers[0].bounding_box().max.Z

        pan2_z = risers1_top_z + GAP_TOLERANCE
        pan2 = pan_geom.translate((0, 0, pan2_z))
        pan2.label = "Pan 2"
        
        pan2_top_z = pan2.bounding_box().max.Z
        
        #RANDOM_NUMBER = 10
        RANDOM_NUMBER = riser_height / 2 - pan_thickness / 2
        risers2_z = pan2_top_z + RANDOM_NUMBER

        for i in [2,3]:
            x = (-100)
            y = (-80 if i % 2 == 0 else 80)
            riser = magnet_geom.rotate(Axis.Z, 90)
            riser = riser.translate((x, y, risers2_z))
            riser.label = "Magnet (Layer 2)"
            risers.append(riser)

        risers2_top_z = risers[2].bounding_box().max.Z

        stopper_magnets = [] 

        x = 132
        y = 0
        magnet1_z = pan2_top_z + RANDOM_NUMBER
        magnet1 = magnet_geom.rotate(Axis.Z, 90)
        magnet1 = magnet1.translate((x, y, magnet1_z))
        magnet1.label = "Stopper magnet 1"
        stopper_magnets.append(magnet1)

        x = 148

        x = magnet1.bounding_box().max.X + (props["riser"]["height"] / 2)

        y = 0
        magnet2_z = pan2_top_z + (props["riser"]["width"]/ 2) - pan_thickness/2
        magnet2 = magnet_geom.rotate(Axis.Z, 90).rotate(Axis.Y, 90)
        magnet2 = magnet2.translate((x, y, magnet2_z))
        magnet2.label = "Stopper magnet 2"
        stopper_magnets.append(magnet2)

        # Place laptop so its bottom is at the top of pan2
        laptop_geom = LaptopComponent(props["laptop"]).render()
        laptop_z = risers2_top_z + laptop_thickness / 2
        laptop = laptop_geom.translate((0, 0, laptop_z))
        laptop = laptop.rotate(Axis.Z, 90)
        laptop.label = "Laptop"

        parts = []
        parts.append(pan1) #, name="pan1")
        parts.append(pan2) #, name="pan2"
        for idx, riser in enumerate(risers):
            parts.append(riser) #, name=f"riser{idx+1}")
        for idx, magnet in enumerate(stopper_magnets):
            parts.append(magnet)
        parts.append(laptop) #, name="laptop")
    
        asm = Compound()
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

