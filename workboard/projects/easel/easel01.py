"""
Easel Model (easel01.py)

- Renders a wooden easel with three legs (A, B, C),
  crossbars (D, E),
  a center post (F),
  lower canvas holder (G),
  Upper canvas holder (H).
- All pieces have a 1/4" (6.35mm) roundover on their non-joined edges.
- Dimensions in inches, converted to mm (1 inch = 25.4 mm).

## TODO
- leg A, B & crossbar gaps
- centerpost crossbar overlap
- angled cuts at meets with Leg A, Leg B

- more advanced canvas holder
- craft paper roll
- drip tray
"""

import math
import os
from math import sqrt, acos, degrees
from typing import Any, Dict, Optional
from build123d import Box, Compound, Axis, fillet, Text, Vector

INCH = 25.4
ROUNDER_RADIUS = 6.35  # 1/4 inch in mm


class Transforms:
    @staticmethod
    def rotate_about_center(obj, axis, angle):
        """Rotate a build123d object about its bounding box center."""
        center = obj.bounding_box().center()
        return obj.translate(-center).rotate(axis, angle).translate(center)

    @staticmethod
    def rotate_about_point(obj, axis, angle, point):
        return obj.translate(-point).rotate(axis, angle).translate(point)

    @staticmethod
    def midpoint_at_floor(obj1, obj2):
        """Return the midpoint (X, Y, Z=0) between the bottom faces of two objects."""
        # Get the bounding box centers of both objects
        c1 = obj1.bounding_box().center()
        c2 = obj2.bounding_box().center()
        # Project to Z=0 (floor)
        p1 = type(c1)(c1.X, c1.Y, 0)
        p2 = type(c2)(c2.X, c2.Y, 0)
        # Midpoint
        mid = type(c1)((p1.X + p2.X) / 2, (p1.Y + p2.Y) / 2, 0)
        return mid
    
    @staticmethod
    def rotate_about_floor(obj, axis, angle, objs: Optional[list] = None):
        """
        Rotate a single object about the floor midpoint (Z=0) of its bounding box or a set of reference objects.
        If objs is provided, use their floor midpoint as the rotation center; otherwise, use obj itself.
        """
        if objs is None:
            floor_point = Transforms.midpoint_at_floor(obj, obj)
        else:
            if len(objs) == 1:
                floor_point = Transforms.midpoint_at_floor(objs[0], objs[0])
            else:
                floor_point = Transforms.midpoint_at_floor(objs[0], objs[1])
                if len(objs) > 2:
                    for o in objs[2:]:
                        floor_point = Transforms.midpoint_at_floor(o, floor_point)
        return Transforms.rotate_about_point(obj, axis, angle, floor_point)


class Walks:
    @staticmethod
    def walk_compound(compound):
        """
        Recursively yield all children of a Compound (including nested Compounds).
        Usage:
            for part in Walks.walk_compound(compound):
                ...
        """
        for child in getattr(compound, 'children', []):
            yield child
            if hasattr(child, 'children'):
                yield from Walks.walk_compound(child)



class Easel:
    def __init__(self, props: Optional[Dict[str, Any]] = None):
        defaults = self.defaultProps()
        self.props = {**defaults, **(props or {})}

    @staticmethod
    def defaultProps():
        return {
            "leg_thickness": 30,
            "leg_width": 40,
            "leg_b_len": 59 * INCH,
            "leg_a_len": 59 * INCH,
            "leg_c_len": 48 * INCH,
            "floor_width": 24 * INCH,
            "centerpost_f_thickness": 25,
            "centerpost_f_width": 30,
            "crossbar_d_height": 20 * INCH,
            "crossbar_e_height": 50 * INCH,
            "crossbar_thickness": 25,
            "crossbar_height": 40,
            "canvas_holder_g_width": 10 * INCH,
            "canvas_holder_g_thickness": 2 * INCH,
            "canvas_holder_g_height": 30,
            "canvas_holder_h_width": 10 * INCH,
            "canvas_holder_h_thickness": 2 * INCH,
            "canvas_holder_h_height": 30,
            # adjustable:
            "canvas_holder_g_yoffset": 50,
            "canvas_holder_h_yoffset": 10*INCH,

            "board1_thickness": 0.25*INCH,
            #"board1_width": 24*INCH,   # inside crossbar D d
            "board1_width": 28*INCH,    # just outside legs (TODO gap)
            # TODO: "board1_length":  then set canvas_holder_y_yoffset from that
            "board1_margin": 0,
        }

    def rounded_box(self, length, width, height, roundover=ROUNDER_RADIUS, label=None):
        box = Box(length, width, height)
        if roundover > 0:
            box = fillet(box.edges(), roundover)
        if label is not None:
            box.label = label
        return box

    def render(self, labelOffset=50) -> Compound:
        p = self.props
        splay_angle = math.degrees(math.atan(p["floor_width"] / (2 * p["leg_b_len"])))

        # A. Leg (L)
        leg_a = self.rounded_box(
            p["leg_a_len"], p["leg_width"], p["leg_thickness"], label="A. Leg (L)"
        )
        leg_a = leg_a.rotate(Axis.Y, 90 - splay_angle)
        leg_a = leg_a.translate((p["floor_width"] / 2, 0, p["leg_a_len"] / 2))

        # B. Leg (R)
        leg_b = self.rounded_box(
            p["leg_b_len"], p["leg_width"], p["leg_thickness"], label="B. Leg (R)"
        )
        leg_b = leg_b.rotate(Axis.Y, 90 + splay_angle)
        leg_b = leg_b.translate(
            (-p["floor_width"] / 2, 0, p["leg_b_len"] / 2)
        )  # Place foot at Z=0

        # C. Leg (rear)
        leg_c = self.rounded_box(
            p["leg_c_len"], p["leg_width"], p["leg_thickness"], label="C. Leg (Rear)"
        )
        leg_c = leg_c.rotate(Axis.Y, 90)
        leg_c = leg_c.translate((0, -p["floor_width"] / 2, p["leg_c_len"] / 2))

        # D. Lower Crossbar (spans between A and B)
        crossbar_width_d = (
            abs(leg_a.bounding_box().center().X - leg_b.bounding_box().center().X)
            + p["leg_width"]
            + 1e-2
        )
        crossbar_d = self.rounded_box(
            crossbar_width_d,
            p["crossbar_thickness"],
            p["crossbar_height"],
            label="D. Lower Crossbar",
        )
        crossbar_d = crossbar_d.translate((0, 0, p["crossbar_d_height"]))

        # E. Upper Crossbar (spans between A and B)
        crossbar_width_e = 13 * INCH
        crossbar_e = self.rounded_box(
            crossbar_width_e,
            p["crossbar_thickness"],
            p["crossbar_height"],
            label="E. Upper Crossbar",
        )
        crossbar_e = crossbar_e.translate((0, 0, p["crossbar_e_height"]))

        # F. Center post (joins D and E; G and H clamp around)
        g_z = p["leg_b_len"] + 10 * INCH  # Z of top rail G
        centerpost_f_len = g_z - p["crossbar_d_height"] + p["canvas_holder_h_height"] / 2
        centerpost_f = self.rounded_box(
            centerpost_f_len, p["centerpost_f_width"], p["centerpost_f_thickness"], label="F. Center post"
        )
        centerpost_f = centerpost_f.rotate(Axis.Y, 90)
        centerpost_f = centerpost_f.translate((0, 0, p["crossbar_d_height"] + centerpost_f_len / 2))

        # centerpost_f = centerpost_f.translate(
        #     (p["floor_width"] / 2, 0, p["leg_a_len"] / 2)
        # )

        # G. Lower canvas holder (adjustable, attaches to F)
        canvas_holder_g = self.rounded_box(
            p["canvas_holder_g_width"],
            p["canvas_holder_g_thickness"],
            p["canvas_holder_g_height"],
            label="G. Lower canvas holder",
        )
        canvas_holder_g = canvas_holder_g.translate(
            (0, p["leg_width"], p["crossbar_d_height"] + p["canvas_holder_g_yoffset"]))

        # H. Upper canvas holder (adjustable, attaches to F)
        canvas_holder_h = self.rounded_box(
            p["canvas_holder_h_width"],
            p["canvas_holder_h_thickness"],
            p["canvas_holder_h_height"],
            label="H. Upper canvas holder (1)",
        )
        canvas_holder_h = canvas_holder_h.translate(
            (0, p["leg_width"], g_z-p["canvas_holder_h_yoffset"]))


        canvas_holder_i = self.rounded_box(
            p["canvas_holder_h_width"],
            p["canvas_holder_h_thickness"],
            p["canvas_holder_h_height"],
            label="H. Upper canvas holder (front)",
        )
        canvas_holder_i = canvas_holder_i.rotate(Axis.X, 90)
        canvas_holder_i = canvas_holder_i.translate(
            (0, -p["leg_thickness"], g_z-p["canvas_holder_h_yoffset"]))
        canvas_holder_i.label = "I. Upper Canvas Holder (rear)"


        # Assemble
        parts_front = [
            leg_a,
            leg_b,
            crossbar_d,
            crossbar_e,
            centerpost_f,
            canvas_holder_g,
            canvas_holder_h,
            canvas_holder_i
        ]

        parts_back = [
            Transforms.rotate_about_floor(leg_c, Axis.X, -12)
        ]

        parts_backboards = [
            self.board_part_between(
                    canvas_holder_g, canvas_holder_h
                ).rotate(Axis.Z, 90)
                .translate((0, p['canvas_holder_g_thickness']/3, 0))
        ]
        parts = [*parts_front, *parts_back, *parts_backboards]

        labels = []
        AMOUNT_IN_FRONT_OR_TODO_BEHIND = 42
        for part in parts:
            label = getattr(part, "label", None)
            if label is None:
                print(f"INFO: {part!r} {part} has no label")
            if label:
                center = part.bounding_box().center()
                # Ray from origin through center
                ray = center.normalized()
                offset = ray * labelOffset
                label_pos = center + offset
                # Place text label at label_pos, facing +Z
                text_obj = Text(label, 40)  # Only set size, not font
                #text_obj.label = f'label:{label.split(None,1)[0].removesuffix(".")}'
                text_obj.label = f'label:{label}'
                text_obj = text_obj.rotate(Axis.X, 90).rotate(Axis.Z, 180)
                text_obj = text_obj.translate((label_pos.X, label_pos.Y+AMOUNT_IN_FRONT_OR_TODO_BEHIND, label_pos.Z))
                labels.append(text_obj)
        
        labels_folder = Compound(
            label="Labels",
            children=labels,
        )
        _asm_front = Compound(
            label="Easel Front",
            children=parts_front
        )
        _asm_back = Compound(
            label="Easel Back",
            children=parts_back
        )
    
        _leg_floor_midpoint = Transforms.midpoint_at_floor(leg_a, leg_b)
        asm_front = Transforms.rotate_about_point(_asm_front, Axis.X, 42, _leg_floor_midpoint)
        asm_back = Transforms.rotate_about_center(_asm_back, Axis.Y, -34)
        
        asm = Compound(
            label="Easel",
            children=[
                asm_front,
                asm_back,
                Compound(label="Board1", children=parts_backboards),
                labels_folder],
        )
        return asm

    def board_part_between(self, g_part, h_part, label='Board1'):
        """Create a canvas part spanning between G and H using board1_* props."""
        p = self.props
        
        # Get the centers of G and H
        g_center = g_part.bounding_box().center()
        h_center = h_part.bounding_box().center()
        
        # Canvas thickness, width, and margin from props
        thickness = p.get("board1_thickness", 0.25*INCH)
        width = p.get("board1_width", 24*INCH)
        margin = p.get("board1_margin", 0)
        
        # The canvas spans from G to H, so its length is the distance between their centers
        dx = h_center.X - g_center.X
        dy = h_center.Y - g_center.Y
        dz = h_center.Z - g_center.Z
        length = (math.sqrt(dx*dx + dy*dy + dz*dz)
                   - 2*margin
                     - (1/2*p['canvas_holder_h_thickness']))

        print(f"board1 length: {length} inches={length/INCH=}")
        
        # The midpoint between G and H
        mid = type(g_center)((g_center.X + h_center.X)/2, (g_center.Y + h_center.Y)/2, (g_center.Z + h_center.Z)/2)
        
        # Create the canvas box centered at origin, then move to mid and align
        box1 = Box(length, width, thickness)
        # Align canvas along the vector from G to H
        v = Vector(dx, dy, dz)
        v_norm = v.normalized()
        # Default canvas is along X, so rotate from X to v
        x_axis = Vector(1, 0, 0)
        if not (abs(v_norm.X - 1) < 1e-6 and abs(v_norm.Y) < 1e-6 and abs(v_norm.Z) < 1e-6):
            rot_axis = x_axis.cross(v_norm)
            rot_angle = math.degrees(math.acos(x_axis.dot(v_norm)))
            if rot_axis.length > 1e-6:
                # Convert rot_axis to Axis for build123d
                axis = Axis((0, 0, 0), (rot_axis.X, rot_axis.Y, rot_axis.Z))
                box1 = box1.rotate(axis, rot_angle)
        # Move to midpoint
        #box1 = box1.translate((mid.X, mid.Y, mid.Z))
        box1 = box1.translate((1*INCH, 0, mid.Z))
        box1.label = label
        return box1


def running_in_vscode():
    return "VSCODE_IPC_HOOK_CLI" in os.environ


def main():
    easel = Easel().render()
    if running_in_vscode():
        from ocp_vscode import show

        show(easel)
    else:
        print(easel)


if __name__ == "__main__":
    main()