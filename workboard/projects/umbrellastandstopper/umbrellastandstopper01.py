
import os
import pprint

from build123d import Cylinder, Sphere, Box, Align, scale, Axis, extrude, Circle


"""
## Names
- umbrella stand stopper
- umbrella cork
- umbrella stand table
- umbrella stand cork

## Ideas
- loop for a
  - string
  - carabiner
- strap around post
- table around post instead of in post
- light(s)
- solar light(s)
"""


class MushroomModes:
    spherical = {"name": "spherical", "params": {}}
    ellipsoid = {"name": "ellipsoid", "params": {}}
    cylinder_holes = {"name": "cylinder_holes", "params": {}}
    cylinder_diamond = {"name": "cylinder_diamond", "params": {}}


def mushroom(
    stem_height:float=76.2,  # 3 inches in mm
    stem_diameter:float=40,  # 40 mm, parametric for umbrella stand inner diameter
    stem_chamfer_length:float=2,

    #mode=MushroomModes.spherical,
    cap_radius:float=40,     # parametric
    cap_height:float|None=None,   # parametric,

    #mode=MushroomModes.ellipsoid,
    #cap_radius=40,     # parametric
    #cap_height=None,   # parametric,
    #cap_flatness=0.7,
    cap_flatness:float=0.2,

    #mode=MushroomModes.cylinder_holes,
    #cap_radius=40,     # parametric
    #cap_height=None,   # parametric,
    #TODO

    mode=MushroomModes.cylinder_diamond,
    #cap_radius=40,     # parametric
    #cap_height=None,   # parametric,
    band_thickness=3,
    lattice_spacing=6,
    lattice_thickness=1.5
):
    # Create the stem (cylinder)
    #stem = Cylinder(stem_diameter / 2, stem_height)
    stem = extrude(Circle(stem_diameter/2), stem_height)
    stem = stem.chamfer(
        edge_list=stem.faces()[1].edges(),
        length=stem_chamfer_length,
        length2=0)


    # Create the cap or table    
    if mode == MushroomModes.spherical:
        # Create the cap (spherical segment)
        if cap_height is None:
            cap_height = cap_radius
        cap = Sphere(radius=cap_radius)
        # Cut the bottom of the cap to make it flat and set cap height
        cap = cap & Box(
            2 * cap_radius, 2 * cap_radius, cap_height,
            align=(Align.CENTER, Align.CENTER, Align.MIN)
        )
    elif mode == MushroomModes.ellipsoid:
        # Create the cap as an ellipsoid by scaling a sphere
        if cap_height is None:
            cap_height = cap_radius * cap_flatness  # default to a "flatter" cap
        # Start with a sphere of radius=cap_radius
        cap = Sphere(radius=cap_radius)
        # Scale the sphere in Z to get the desired cap_height
        scale_z = cap_height / cap_radius
        cap = scale(cap, (1, 1, scale_z))
        # Cut the bottom of the cap to make it flat and set cap height
        cap = cap & Box(
            2 * cap_radius, 2 * cap_radius, cap_height,
            align=(Align.CENTER, Align.CENTER, Align.MIN)
        )
    elif mode == MushroomModes.cylinder_holes:
        # Create the cap as a cylinder
        if cap_height is None:
            cap_height = 25.4/8  # TODO  # default to a "flatter" cap
        # Start with a cylinder of radius=cap_radius
        cap = Cylinder(radius=cap_radius, height=cap_height)

        # Add a grid of circular holes through the cap
        # Parameters for holes
        hole_radius = 3  # mm
        hole_spacing = 15  # mm
        num_x = int((2 * cap_radius) // hole_spacing)
        num_y = int((2 * cap_radius) // hole_spacing)


        holes = []
        for i in range(-num_x // 2, num_x // 2 + 1):
            for j in range(-num_y // 2, num_y // 2 + 1):
                x = i * hole_spacing
                y = j * hole_spacing
                # Only add holes within the cap's circular area
                if x**2 + y**2 <= (cap_radius - hole_radius)**2:
                    hole = Cylinder(radius=hole_radius, height=cap_height*2.2)
                    hole = hole.translate((x, y, cap_height / 2))
                    holes.append(hole)

        # Subtract holes from cap
        for hole in holes:
            cap = cap - hole

    elif mode == MushroomModes.cylinder_diamond:
        # Create the cap as a cylinder
        if cap_height is None:
            cap_height = 25.4/8  # TODO  # default to a "flatter" cap
        # Start with a cylinder of radius=cap_radius height=cap_height
        cap = Cylinder(radius=cap_radius, height=cap_height)
        # Outer band (cylinder ring)
        band = Cylinder(
            radius=cap_radius,
            height=band_thickness,
            align=Align.CENTER
        ) - Cylinder(
            radius=cap_radius - band_thickness,
            height=band_thickness + 1,
            align=Align.CENTER
        )
        band = band.translate((0, 0, cap_height - band_thickness / 2))

        # Lattice grid (diamond pattern)
        lattice = None
        z = cap_height - band_thickness
        axis = Axis.Z
        for angle in [(20), (-20)]:
            for x in range(-int(cap_radius), int(cap_radius) + 1, lattice_spacing):
                rod = Box(
                    lattice_thickness,
                    2 * cap_radius + 2,
                    band_thickness,
                    align=(Align.CENTER, Align.CENTER, Align.MIN))
                rod = rod.translate((x, 0, z))
                rod = rod.rotate(axis, angle)
                #rod = rod.translate((0, 0, z + zoffset))
                rod = rod & Cylinder(radius=cap_radius - lattice_thickness / 2, height=cap_height)
                lattice = rod if lattice is None else lattice + rod

        # Combine band and lattice
        cap = band + lattice

    else:
        raise ValueError(f"Unknown mode. mode={mode!r}")
    # Move cap to sit on top of stem
    cap = cap.translate((0, 0, stem_height))
    # Combine stem and cap
    mushroom = stem + cap
    return mushroom



def running_in_vscode() -> bool:
    return "VSCODE_IPC_HOOK_CLI" in os.environ


def main() -> int:
    #obj = Workboard(id=1, name="workboard01")
    obj = mushroom
    # obj.init()
    # data = obj.render()

    data = {}

    # do_export_files = True
    # if do_export_files:
    #     data["export_part_filenames"] = export_files(
    #         filenameprefixsuffix="part", partsiterable=data["parts"].items()
    #     )
    #     data["export_assembly_filenames"] = export_files(
    #         filenameprefixsuffix="assembly", partsiterable=data["assemblies"].items()
    #     )

    print("DEBUG: pprint(data)=")
    pprint.pprint(data, sort_dicts=False)


    # Example: 3" stem, 30mm diameter, 40mm cap radius, 25mm cap height
    # Export as STEP
    objs = []
    ##m1 = mushroom(mode=MushroomModes.spherical, stem_height=76.2, stem_diameter=40, cap_radius=60) #, cap_height=25)
    ##m1 = mushroom(mode=MushroomModes.spherical, stem_height=76.2, stem_diameter=40, cap_radius=90) #, cap_height=25)
    #m1 = mushroom(mode=MushroomModes.spherical, stem_height=76.2, stem_diameter=40, cap_radius=120) #, cap_height=25)
    m1 = mushroom(mode=MushroomModes.ellipsoid, stem_height=76.2, stem_diameter=40, cap_radius=60) #, cap_height=25)
    #m1 = mushroom(mode=MushroomModes.cylinder_holes, stem_height=76.2, stem_diameter=40, cap_radius=60) #, cap_height=25)
    #m1 = mushroom(mode=MushroomModes.cylinder_diamond, stem_height=76.2, stem_diameter=40, cap_radius=60) #, cap_height=25)
    
    objs.append(m1)
    #objs.append(m2)

    if running_in_vscode():
        # ocp_vscode is used to visualize the model in VSCode
        # Install the "OCP CAD Viewer" extension in VSCode to view the model
        from ocp_vscode import show
        for obj in objs:
            show(obj)

    return 0


if __name__ == "__main__":
    main()
