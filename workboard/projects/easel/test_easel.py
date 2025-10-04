"""
test_easel.py
"""
import math
import pytest
from build123d import Compound  #, Axis
from workboard.projects.easel.easel01 import Easel, INCH, Walks

# --- build123d test helpers ---
def _get_child_by_label(compound, label):
    # Recursively search for a child whose label starts with the given label + '. '
    for child in getattr(compound, 'children', []):
        child_label = getattr(child, 'label', None)
        if child_label is not None and child_label.startswith(label + ". "):
            return child
        # If the child is a Compound, search recursively
        if hasattr(child, 'children'):
            found = _get_child_by_label(child, label)
            if found is not None:
                return found
    return None

def get_child_by_label(compound, label):
    obj = _get_child_by_label(compound, label)
    assert obj is not None, f"Part with label starting with '{label}. ' not found in assembly"
    return obj


def collect_labels(compound, labels=None):
    if labels is None:
        labels = []
    for child in getattr(compound, 'children', []):
        label = getattr(child, 'label', None)
        if label is not None:
            labels.append(label)
        if hasattr(child, 'children'):
            collect_labels(child, labels)
    return labels


# --- build123d spatial test helpers ---
def assert_centers_close(obj1, obj2, axes="XYZ", tol=1e-2):
    c1 = obj1.bounding_box().center()
    c2 = obj2.bounding_box().center()
    if "X" in axes:
        assert abs(c1.X - c2.X) < tol, f"X centers not close: {c1.X} vs {c2.X}"
    if "Y" in axes:
        assert abs(c1.Y - c2.Y) < tol, f"Y centers not close: {c1.Y} vs {c2.Y}"
    if "Z" in axes:
        assert abs(c1.Z - c2.Z) < tol, f"Z centers not close: {c1.Z} vs {c2.Z}"

def assert_bbox_contains(obj, point, axes="XYZ"):
    bbox = obj.bounding_box()
    if "X" in axes:
        assert bbox.min.X <= point.X <= bbox.max.X, f"X {point.X} not in [{bbox.min.X}, {bbox.max.X}]"
    if "Y" in axes:
        assert bbox.min.Y <= point.Y <= bbox.max.Y, f"Y {point.Y} not in [{bbox.min.Y}, {bbox.max.Y}]"
    if "Z" in axes:
        assert bbox.min.Z <= point.Z <= bbox.max.Z, f"Z {point.Z} not in [{bbox.min.Z}, {bbox.max.Z}]"

def assert_bbox_overlap(obj1, obj2, axes="XYZ"):
    b1 = obj1.bounding_box()
    b2 = obj2.bounding_box()
    if "X" in axes:
        assert b1.max.X >= b2.min.X and b2.max.X >= b1.min.X, f"No X overlap: {b1} vs {b2}"
    if "Y" in axes:
        assert b1.max.Y >= b2.min.Y and b2.max.Y >= b1.min.Y, f"No Y overlap: {b1} vs {b2}"
    if "Z" in axes:
        assert b1.max.Z >= b2.min.Z and b2.max.Z >= b1.min.Z, f"No Z overlap: {b1} vs {b2}"

def assert_bbox_top_covers_center(obj, target_obj, axes="Z"):
    """
    Assert that the top (max along axes) of obj's bounding box is at or above the center of target_obj along the given axes.
    """
    bbox = obj.bounding_box()
    target_center = target_obj.bounding_box().center()
    if "X" in axes:
        assert bbox.max.X >= target_center.X, f"Top X {bbox.max.X} does not cover center X {target_center.X}"
    if "Y" in axes:
        assert bbox.max.Y >= target_center.Y, f"Top Y {bbox.max.Y} does not cover center Y {target_center.Y}"
    if "Z" in axes:
        assert bbox.max.Z >= target_center.Z, f"Top Z {bbox.max.Z} does not cover center Z {target_center.Z}"


# --- test assertions ---

def test_easel_default_props():
    easel = Easel()
    props = easel.props
    assert isinstance(props, dict)
    assert props['leg_a_len'] == pytest.approx(59 * INCH)
    assert props['leg_c_len'] == pytest.approx(48 * INCH)
    assert props['floor_width'] == pytest.approx(24 * INCH)
    assert props['leg_thickness'] > 0
    assert props['leg_width'] > 0

def test_easel_render_returns_compound():
    easel = Easel()
    model = easel.render()
    assert isinstance(model, Compound)
    assert hasattr(model, 'children')
    assert len(model.children) == 4
    #labels = [getattr(child, 'label', None) for child in Walks.walk_compound(model)]
    labels = collect_labels(model)
    for label in ["A", "B", "C", "D", "E", "F", "G", "H", "I"]:
        assert any(l.startswith(label + ". ") for l in labels), label

def test_easel_custom_props():
    custom = {'leg_a_len': 1000, 'leg_b_len': 1000}
    easel = Easel(props=custom)
    assert easel.props['leg_a_len'] == 1000
    assert easel.props['leg_b_len'] == 1000
    model = easel.render()
    assert isinstance(model, Compound)

def test_legs_a_b_lean_toward_c():
    easel = Easel()
    model = easel.render()
    leg_a = get_child_by_label(model, "A")
    leg_b = get_child_by_label(model, "B")
    leg_c = get_child_by_label(model, "C")
    # Z: top of A/B > top of C (lean toward C)
    assert_bbox_top_covers_center(leg_a, leg_c, axes="Z")
    assert_bbox_top_covers_center(leg_b, leg_c, axes="Z")
    # X: A left, B right, C centered
    assert leg_a.bounding_box().center().X < 0
    assert leg_b.bounding_box().center().X > 0
    assert abs(leg_c.bounding_box().center().X) < 1e-3
    # Y: all in same Y plane (within tol)
    assert_centers_close(leg_a, leg_c, axes="Y")
    assert_centers_close(leg_b, leg_c, axes="Y")

def test_crossbars_meet_legs():
    easel = Easel()
    model = easel.render()
    leg_a = get_child_by_label(model, "A")
    leg_b = get_child_by_label(model, "B")
    crossbar_d = get_child_by_label(model, "D")
    crossbar_e = get_child_by_label(model, "E")
    # Z: crossbars at correct heights
    assert_centers_close(crossbar_d, leg_a, axes="Z", tol=1*INCH)
    assert_centers_close(crossbar_e, leg_a, axes="Z", tol=1*INCH)
    # X: crossbar D spans A/B, E is centered
    assert_bbox_contains(crossbar_d, leg_a.bounding_box().center(), axes="X")
    assert_bbox_contains(crossbar_d, leg_b.bounding_box().center(), axes="X")
    # Y: all in same Y plane
    assert_centers_close(crossbar_d, leg_a, axes="Y")
    assert_centers_close(crossbar_e, leg_a, axes="Y")

def test_leg_f_joins_crossbars():
    easel = Easel()
    model = easel.render()
    leg_f = get_child_by_label(model, "F")
    crossbar_d = get_child_by_label(model, "D")
    # F starts at D in Z, is close in X/Y
    assert_bbox_contains(leg_f, crossbar_d.bounding_box().center(), axes="Z")
    assert_centers_close(leg_f, crossbar_d, axes="X")
    assert_centers_close(leg_f, crossbar_d, axes="Y")

def test_leg_f_through_d_e_g():
    easel = Easel()
    model = easel.render()
    leg_f = get_child_by_label(model, "F")
    crossbar_d = get_child_by_label(model, "D")
    crossbar_e = get_child_by_label(model, "E")
    top_rail_g = get_child_by_label(model, "G")
    # F min Z at D, max Z at/above E and G
    assert_bbox_contains(leg_f, crossbar_d.bounding_box().center(), axes="Z")
    assert_bbox_top_covers_center(leg_f, crossbar_e, axes="Z")
    assert_bbox_top_covers_center(leg_f, top_rail_g, axes="Z")
    # X/Y: F, D, E, G all aligned
    assert_centers_close(leg_f, crossbar_d, axes="X")
    assert_centers_close(leg_f, crossbar_e, axes="X")
    assert_centers_close(leg_f, top_rail_g, axes="X")
    assert_centers_close(leg_f, crossbar_d, axes="Y")
    assert_centers_close(leg_f, crossbar_e, axes="Y")
    assert_centers_close(leg_f, top_rail_g, axes="Y")

def test_crossbar_e_is_16_in():
    easel = Easel()
    model = easel.render()
    crossbar_e = get_child_by_label(model, "E")
    width = crossbar_e.bounding_box().max.X - crossbar_e.bounding_box().min.X
    assert width == pytest.approx(16 * INCH, abs=0.1)

def test_legs_a_b_join_crossbars():
    easel = Easel()
    model = easel.render()
    leg_a = get_child_by_label(model, "A")
    leg_b = get_child_by_label(model, "B")
    crossbar_d = get_child_by_label(model, "D")
    # Only require that the X center of legs A and B is within the X span of crossbar D (not E)
    min_x = crossbar_d.bounding_box().min.X
    max_x = crossbar_d.bounding_box().max.X
    a_x = leg_a.bounding_box().center().X
    b_x = leg_b.bounding_box().center().X
    assert min_x < a_x < max_x
    assert min_x < b_x < max_x

def test_legs_a_b_join_crossbars_xyz():
    easel = Easel()
    model = easel.render()
    leg_a = get_child_by_label(model, "A")
    leg_b = get_child_by_label(model, "B")
    crossbar_d = get_child_by_label(model, "D")
    # X: leg centers within crossbar D's X span
    assert_bbox_contains(crossbar_d, leg_a.bounding_box().center(), axes="X")
    assert_bbox_contains(crossbar_d, leg_b.bounding_box().center(), axes="X")
    # Y: leg and crossbar Y centers should be close (same plane)
    assert_centers_close(leg_a, crossbar_d, axes="Y")
    assert_centers_close(leg_b, crossbar_d, axes="Y")
    # Z: crossbar D's Z center should be within leg A/B Z span
    assert_bbox_contains(leg_a, crossbar_d.bounding_box().center(), axes="Z")
    assert_bbox_contains(leg_b, crossbar_d.bounding_box().center(), axes="Z")

def test_part_labels_are_offset():
    easel = Easel()
    model = easel.render(labelOffset=100)
    # Collect all part label prefixes
    part_labels = collect_labels(model)
    # Recursively collect all label objects with a 'text' attribute
    label_texts = [child for child in Walks.walk_compound(model) if hasattr(child, 'text')]
    found_labels = set(getattr(label, 'text', None) for label in label_texts)
    for label in part_labels:
        assert any(lbl is not None and lbl.startswith(label + ". ") for lbl in found_labels), f"Label '{label}' not found in model labels: {found_labels}"
    # Check that each label is offset from its part center
    for label in label_texts:
        label_str = getattr(label, 'text', None)
        # Find the part with a matching prefix
        part = None
        for candidate in Walks.walk_compound(model):
            part_label = getattr(candidate, 'label', None)
            if part_label and label_str and part_label.startswith(label_str):
                part = candidate
                break
        if part is not None:
            part_center = part.bounding_box().center()
            label_center = label.bounding_box().center()
            dist = (label_center - part_center).Length
            assert dist > 50, f"Label '{label_str}' is not offset from part center: dist={dist}"


def test_board1_centered_between_g_and_h():
    easel = Easel()
    p = easel.props
    # Create G and H parts
    g = easel.rounded_box(
        p["canvas_holder_g_width"],
        p["canvas_holder_g_thickness"],
        p["canvas_holder_g_height"],
        label="G. Lower canvas holder",
    ).translate((0, p["leg_width"], p["crossbar_d_height"] + p["canvas_holder_g_yoffset"]))
    h = easel.rounded_box(
        p["canvas_holder_h_width"],
        p["canvas_holder_h_thickness"],
        p["canvas_holder_h_height"],
        label="H. Upper canvas holder (1)",
    ).translate((0, p["leg_width"], p["leg_b_len"] + 10 * 25.4 - p["canvas_holder_h_yoffset"]))
    # Create Board1
    board1 = easel.board_part_between(g, h, label="Board1")
    # Get centers
    g_center = g.bounding_box().center()
    h_center = h.bounding_box().center()
    board1_center = board1.bounding_box().center()
    # Assert X center is between G and H (within tolerance)
    expected_x = (g_center.X + h_center.X) / 2
    assert math.isclose(board1_center.X, expected_x, abs_tol=1e-6), f"Board1 X center {board1_center.X} != expected {expected_x}"


def test_no_duplicate_labels():
    easel = Easel()
    model = easel.render()
    labels = collect_labels(model)
    # Only check for duplicates among main part labels (A, B, C, D, E, F, G, H, I) by prefix
    main_prefixes = ["A", "B", "C", "D", "E", "F", "G", "H", "I"]
    seen = set()
    duplicates = set()
    for prefix in main_prefixes:
        matches = [lbl for lbl in labels if lbl.startswith(prefix + ".")]
        if len(matches) > 1:
            duplicates.add(prefix)
    assert not duplicates, f"Duplicate main part label prefixes found: {duplicates}"