"""
Centralized default props for all pizzapancoolingmat components.

This file is intended to be imported at the top level of each module that needs defaults.
Avoid importing from pizzapancoolingmat.py or other component modules here to prevent circular imports.
"""

from pydantic import BaseModel, Field, JsonValue

# UNIT_MM = {"unit": "mm"}
# UNIT_MM: dict[str, str] = {"unit": "mm"}
UNIT_MM_AND_REQUIRED: dict[str, JsonValue] = {"unit": "mm", "_required": True}

INCH = 25.4


class PanModel(BaseModel):
    diameter: float = Field(
        ...,
        description="Diameter of the pizza pan in mm.",
        json_schema_extra=UNIT_MM_AND_REQUIRED,
    )
    thickness: float = Field(
        3,
        description="Thickness of the pizza pan in mm.",
        json_schema_extra=UNIT_MM_AND_REQUIRED,
    )
    rim_height: float = Field(
        10,
        description="Height of the pan rim in mm.",
        json_schema_extra=UNIT_MM_AND_REQUIRED,
    )


class RiserModel(BaseModel):
    length: float = Field(
        (1 + (7 / 8)) * INCH,
        description="Length of the riser in mm.",
        json_schema_extra=UNIT_MM_AND_REQUIRED,
    )
    width: float = Field(
        (7/8)*INCH,
        description="Width of the riser in mm.",
        json_schema_extra=UNIT_MM_AND_REQUIRED,
    )
    height: float = Field(
        (3/8)*INCH,
        description="Height of the riser in mm.",
        json_schema_extra=UNIT_MM_AND_REQUIRED,
    )


class LaptopModel(BaseModel):
    length: float = Field(
        360,
        description="Length of the laptop in mm.",
        json_schema_extra=UNIT_MM_AND_REQUIRED,
    )
    width: float = Field(
        250,
        description="Width of the laptop in mm.",
        json_schema_extra=UNIT_MM_AND_REQUIRED,
    )
    thickness: float = Field(
        18,
        description="Thickness of the laptop in mm.",
        json_schema_extra=UNIT_MM_AND_REQUIRED,
    )


INCH = 25.4  # mm

# Centralized default sets for easy extension
DEFAULTS = {
    "default0": {
        "pan": PanModel(diameter=330, thickness=3, rim_height=2).model_dump(),
        # "riser": RiserModel(length=40, width=20, height=20).model_dump(),
        "riser": RiserModel(
            length=(1 + (7 / 8)) * INCH,
            width=(7 / 8) * INCH,
            height=(3 / 8) * INCH
        ).model_dump(),
        "laptop": LaptopModel(length=360, width=250, thickness=18).model_dump(),
    }
}

from pprint import pprint
print("DEFAULTS: ")
pprint(DEFAULTS)