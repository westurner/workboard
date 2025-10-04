#!/usr/bin/env python3
"""
pizzapancoolingmat.main
"""
import argparse
import json
import os
import pprint
import sys

try:
    from pydantic_core import PydanticUndefined
except ImportError:
    try:
        from pydantic._internal._core import PydanticUndefined # type: ignore
    except ImportError:
        PydanticUndefined = None  # fallback, should not happen

from workboard.projects.pizzapancoolingmat.pizzapancoolingmat import PizzaPanCoolingMatAssembly
from workboard.projects.pizzapancoolingmat.schemas import DEFAULTS, PanModel, RiserModel, LaptopModel


def run_with_args(args: list[str] | None = None, cls=PizzaPanCoolingMatAssembly):
    parser = argparse.ArgumentParser(
        description="""
        Render PizzaPanCoolingMatAssembly.
        
        Usage examples:
          %(prog)s --list-props
          %(prog)s --list-props-schema
          %(prog)s --props default0 --pan-diameter 350 --show
        """,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        '--list-props',
        action='store_true',
        help='Print a summary of all available prop sets and exit. Shows schema and raw props.'
    )
    parser.add_argument(
        '--list-props-schema',
        action='store_true',
        help='Pretty-print the JSON schema for all Pydantic models and exit.'
    )
    parser.add_argument(
        '--props',
        type=str,
        default='default0',
        help="Which set of props to use (default: 'default0'). Use --list-props to see available sets."
    )
    parser.add_argument(
        '--show',
        action='store_true',
        help='Show the rendered assembly in the OCP CAD Viewer (VS Code only).'
    )

    # Always add all possible prop CLI arguments for all models, using model defaults
    MODEL_MAP = {"pan": PanModel, "riser": RiserModel, "laptop": LaptopModel}
    for group, model in MODEL_MAP.items():
        for key, field in model.model_fields.items():
            arg_name = f'--{group}-{key.replace("_", "-")}'
            desc = field.description or ""
            unit = field.json_schema_extra.get("unit") if field.json_schema_extra else None
            unit_str = f" ; unit: {unit} ;" if unit else ""
            default = field.default
            kwargs = {}
            if default is not PydanticUndefined:
                kwargs["default"] = default
                kwargs["type"] = type(default)
            else:
                kwargs["type"] = str
            parser.add_argument(
                arg_name,
                help=f"{desc} (default: {default}{unit_str} group: {group})",
                **kwargs
            )
    # Now parse args (do not call parse_known_args before this)
    parsed = parser.parse_args(args)

    if parsed.list_props:
        print("\n=== PROPS SCHEMA ===")
        for group, model in MODEL_MAP.items():
            print(f"[{group}]")
            for key, field in model.model_fields.items():
                print(f"  {key} ({field.annotation.__name__}): {field.description} (default: {field.default})")
            print()
        print("=== RAW PROPS ===")
        pprint.pprint(DEFAULTS)
        exit(0)

    if parsed.list_props_schema:
        print("\n=== PROPS JSON SCHEMA ===")
        for group, model in MODEL_MAP.items():
            print(f"[{group}] JSON Schema:")
            print(json.dumps(model.model_json_schema(), indent=2))
            print()
        exit(0)

    props_set = parsed.props  # Already set above
    try:
        props = DEFAULTS[props_set]
    except KeyError:
        print(f"[ERROR] Prop set '{props_set}' not found in PROPS", file=sys.stderr)
        sys.exit(1)

    print(f"\n=== PROPS FOR SET '{props_set}' ===")
    pprint.pprint(props)

    # Build props dicts for each group, ensuring all required fields are present
    props_dict = {}
    for group, model in MODEL_MAP.items():
        group_dict = {}
        group_props = props.get(group, {})
        for key in model.model_fields:
            arg_name = f'{group}_{key}'
            cli_value = getattr(parsed, arg_name, None)
            if cli_value is not None:
                group_dict[key] = cli_value
            elif key in group_props:
                group_dict[key] = group_props[key]
            # else: leave missing, so Pydantic will raise if required
        props_dict[group] = group_dict

    # Validate props_dict using Pydantic models
    try:
        props_dict["pan"] = PanModel(**props_dict["pan"]).model_dump()
        props_dict["riser"] = RiserModel(**props_dict["riser"]).model_dump()
        props_dict["laptop"] = LaptopModel(**props_dict["laptop"]).model_dump()
    except Exception as e:
        print("\n[ERROR] Invalid props:", e, file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)

    assembly = cls(props_dict)
    asm = assembly.render()
    if parsed.show:
        from ocp_vscode import show
        show(asm)
    return asm


def running_in_vscode() -> bool:
    return "VSCODE_IPC_HOOK_CLI" in os.environ


def main(args):
    objects = []
    assembly1 = run_with_args(args)
    objects.append(assembly1)

    if running_in_vscode():
        # ocp_vscode is used to visualize the model in VSCode
        # Install the "OCP CAD Viewer" extension in VSCode to view the model
        from ocp_vscode import show
        for obj in objects:
            show(obj)
    else:
        for obj in objects:
            print(obj)

if __name__ == "__main__":
    import sys
    main(sys.argv[1:])
