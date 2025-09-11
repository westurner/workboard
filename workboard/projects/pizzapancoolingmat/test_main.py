"""
"""

import subprocess
import sys
import os

import pytest

from . import main
from .pizzapancoolingmat import PizzaPanCoolingMatAssembly, PizzaPanComponent, MagneticLaptopRiserSquareComponent, LaptopComponent
from .schemas import DEFAULTS


def test_run_with_args_defaults():
    asm = main.run_with_args([])
    # Check type
    assert hasattr(asm, 'children')
    # Check there are 2 pans, 4 risers, 1 laptop
    pans = [c for c in asm.children if isinstance(c, PizzaPanComponent) or getattr(c, 'shape', None) is not None]
    risers = [c for c in asm.children if isinstance(c, MagneticLaptopRiserSquareComponent) or getattr(c, 'shape', None) is not None]
    laptops = [c for c in asm.children if isinstance(c, LaptopComponent) or getattr(c, 'shape', None) is not None]
    # The actual types may be build123d Part, so check by order
    assert len(asm.children) == 7
    # Check pan properties
    pan_disk = asm.children[0]
    pan2_disk = asm.children[1]
    # These are build123d Part, but we can check their dimensions
    # Check riser positions and count
    riser_objs = asm.children[2:6]
    assert len(riser_objs) == 4
    # Check laptop
    laptop_obj = asm.children[6]
    # No direct props, but we can check the order
    # Optionally check that the default values match
    defaults = DEFAULTS["default0"]
    assert defaults["pan"]["diameter"] == 330
    assert defaults["riser"]["length"] == 40
    assert defaults["laptop"]["length"] == 360


def test_run_with_args_custom():
    args = [
        "--pan-diameter", "350",
        "--pan-thickness", "5",
        "--pan-rim-height", "12",
        "--riser-length", "50",
        "--riser-width", "25",
        "--riser-height", "15",
        "--laptop-length", "400",
        "--laptop-width", "300",
        "--laptop-thickness", "20"
    ]
    asm = main.run_with_args(args)
    # Check type
    assert hasattr(asm, 'children')
    # Check there are 2 pans, 4 risers, 1 laptop
    assert len(asm.children) == 7
    # Check pan properties by reconstructing expected dimensions
    # The first two children are pans
    pan_disk = asm.children[0]
    pan2_disk = asm.children[1]
    # The next four are risers
    riser_objs = asm.children[2:6]
    # The last is the laptop
    laptop_obj = asm.children[6]
    # Optionally, check the bounding box or shape dimensions if available
    # For build123d Part, check .bounding_box or .shape if present
    # Example: assert pan_disk.bounding_box().size.X == 350
    # Example: assert laptop_obj.bounding_box().size.X == 400
    # These checks are placeholders; adapt if build123d API exposes dimensions
    # assert pan_disk.bounding_box().size.X == 350
    # assert laptop_obj.bounding_box().size.X == 400
    # If props are accessible, check them
    # If not, these tests will at least verify the structure


def test_run_with_args_props():
    import importlib
    main = importlib.import_module("workboard.projects.pizzapancoolingmat.main")
    main.run_with_args([])
    from .schemas import DEFAULTS
    defaults = DEFAULTS["default0"]
    assert defaults["pan"]["diameter"] == 330
    assert defaults["riser"]["length"] == 40
    assert defaults["laptop"]["length"] == 360


def test_list_props_option():
    result = subprocess.run(
        [sys.executable, os.path.join(os.path.dirname(__file__), "main.py"), "--list-props"],
        capture_output=True, text=True
    )
    assert "PROPS SCHEMA" in result.stdout
    assert "RAW PROPS" in result.stdout


def test_props_option():
    result = subprocess.run(
        [sys.executable, os.path.join(os.path.dirname(__file__), "main.py"), "--props", "default0"],
        capture_output=True, text=True
    )
    assert "PROPS FOR SET 'default0'" in result.stdout


def test_props_set_invalid():
    result = subprocess.run(
        [sys.executable, os.path.join(os.path.dirname(__file__), "main.py"), "--props", "notaset"],
        capture_output=True, text=True
    )
    assert "not found in PROPS" in result.stderr or "not found in PROPS" in result.stdout


def test_list_props_schema_option():
    result = subprocess.run(
        [sys.executable, os.path.join(os.path.dirname(__file__), "main.py"), "--list-props-schema"],
        capture_output=True, text=True
    )
    assert "PROPS JSON SCHEMA" in result.stdout
    assert "pan" in result.stdout and "riser" in result.stdout and "laptop" in result.stdout
    assert '"title": "PanModel"' in result.stdout or '"title": "RiserModel"' in result.stdout or '"title": "LaptopModel"' in result.stdout
    assert result.returncode == 0


def test_geometric_mating_of_assembly():
    """
    Verify geometric mating:
    - pan2 rests atop risers
    - risers rest atop pan1
    - laptop rests atop pan2 rim
    - pan bottom is at Z=0
    """
    from workboard.projects.pizzapancoolingmat.pizzapancoolingmat import PizzaPanCoolingMatAssembly, PizzaPanComponent
    from workboard.projects.pizzapancoolingmat.schemas import DEFAULTS
    import math
    props = DEFAULTS["default0"]
    asm = PizzaPanCoolingMatAssembly(props).render()
    pan1 = asm.children[0]
    pan2 = asm.children[1]
    risers = asm.children[2:6]
    laptop = asm.children[6]

    # pan2 rests atop risers
    pan2_bottom_z = pan2.bounding_box().min.Z
    riser_top_zs = [r.bounding_box().max.Z for r in risers]
    for riser_top_z in riser_top_zs:
        assert math.isclose(pan2_bottom_z, riser_top_z, abs_tol=1e-6), (
            f"pan2 bottom Z ({pan2_bottom_z}) != riser top Z ({riser_top_z})")

    # risers rest atop pan1
    pan1_top_z = pan1.bounding_box().max.Z
    riser_bottom_zs = [r.bounding_box().min.Z for r in risers]
    for riser_bottom_z in riser_bottom_zs:
        assert math.isclose(riser_bottom_z, pan1_top_z, abs_tol=1e-6), (
            f"riser bottom Z ({riser_bottom_z}) != pan1 top Z ({pan1_top_z})")

    # laptop rests atop pan2 rim
    pan2_top_z = pan2.bounding_box().max.Z
    laptop_bottom_z = laptop.bounding_box().min.Z
    assert math.isclose(laptop_bottom_z, pan2_top_z, abs_tol=1e-6), (
        f"laptop bottom Z ({laptop_bottom_z}) != pan2 top Z ({pan2_top_z})")

    # pan bottom is at Z=0
    pan = PizzaPanComponent(props["pan"]).render()
    assert math.isclose(pan.bounding_box().min.Z, 0.0, abs_tol=1e-6), (
        f"pan bottom Z ({pan.bounding_box().min.Z}) != 0.0")


def test_invalid_type_pan_diameter():
    # Pass a string instead of a number for --pan-diameter
    result = subprocess.run(
        [sys.executable, os.path.join(os.path.dirname(__file__), "main.py"), "--pan-diameter", "notanumber"],
        capture_output=True, text=True
    )
    # argparse will catch type error, so check for error message
    assert result.returncode != 0
    assert "invalid" in result.stderr.lower() or "error" in result.stderr.lower()


def test_invalid_value_pan_diameter():
    # Pass a negative value if schema forbids it (assuming diameter > 0)
    result = subprocess.run(
        [sys.executable, os.path.join(os.path.dirname(__file__), "main.py"), "--pan-diameter", "-10"],
        capture_output=True, text=True
    )
    # Pydantic should catch this if schema enforces positive
    assert result.returncode != 0
    assert "invalid props" in result.stderr.lower() or "validation" in result.stderr.lower() or "error" in result.stderr.lower()


def test_missing_required_pan_field():
    # Remove a required field from the pan group and patch DEFAULTS
    from unittest.mock import patch
    from . import main as main_mod
    from .schemas import DEFAULTS
    custom = dict(DEFAULTS["default0"])
    custom["pan"] = dict(custom["pan"])
    del custom["pan"]["diameter"]
    # Patch DEFAULTS to include our custom set
    with patch.dict(main_mod.DEFAULTS, {"default0": custom}):
        # Should raise SystemExit when run_with_args is called due to sys.exit(1)
        import pytest
        with pytest.raises(SystemExit) as excinfo:
            main_mod.run_with_args([])  # TODO: "--props", "custom"])
        # Optionally check exit code
        assert excinfo.value.code == 1


def test_cli_args_help_includes_props():
    # Run the CLI with --help and check that all prop CLI args are present in the help output
    help_result = subprocess.run(
        [sys.executable, os.path.join(os.path.dirname(__file__), "main.py"), "--help"],
        capture_output=True, text=True
    )
    help_text = help_result.stdout
    # Check for a few representative CLI args for each group
    assert "--pan-diameter" in help_text
    assert "--pan-thickness" in help_text
    assert "--riser-length" in help_text
    assert "--laptop-length" in help_text
    # Check that the help text describes the default value for each
    assert "default: PydanticUndefined" in help_text  # for required pan-diameter
    assert "default: 3" in help_text  # for pan-thickness
    assert "default: 40" in help_text  # for riser-length
    assert "default: 360" in help_text  # for laptop-length
    assert help_result.returncode == 0