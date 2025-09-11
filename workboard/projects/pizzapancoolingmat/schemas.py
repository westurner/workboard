"""
Centralized default props for all pizzapancoolingmat components.

This file is intended to be imported at the top level of each module that needs defaults.
Avoid importing from pizzapancoolingmat.py or other component modules here to prevent circular imports.
"""
from pydantic import BaseModel, Field, JsonValue

# UNIT_MM = {"unit": "mm"}
# UNIT_MM: dict[str, str] = {"unit": "mm"}
UNIT_MM: dict[str, JsonValue] = {"unit": "mm", "_required": True}

class PanModel(BaseModel):
    diameter: int = Field(..., description="Diameter of the pizza pan in mm.", json_schema_extra=UNIT_MM)
    thickness: int = Field(3, description="Thickness of the pizza pan in mm.", json_schema_extra=UNIT_MM)
    rim_height: int = Field(10, description="Height of the pan rim in mm.", json_schema_extra=UNIT_MM)

class RiserModel(BaseModel):
    length: int = Field(40, description="Length of the riser in mm.", json_schema_extra=UNIT_MM)
    width: int = Field(20, description="Width of the riser in mm.", json_schema_extra=UNIT_MM)
    height: int = Field(20, description="Height of the riser in mm.", json_schema_extra=UNIT_MM)

class LaptopModel(BaseModel):
    length: int = Field(360, description="Length of the laptop in mm.", json_schema_extra=UNIT_MM)
    width: int = Field(250, description="Width of the laptop in mm.", json_schema_extra=UNIT_MM)
    thickness: int = Field(18, description="Thickness of the laptop in mm.", json_schema_extra=UNIT_MM)

# Centralized default sets for easy extension
DEFAULTS = {
    "default0": {
        "pan": PanModel(diameter=330, thickness=3, rim_height=10).model_dump(),
        "riser": RiserModel(length=40, width=20, height=20).model_dump(),
        "laptop": LaptopModel(length=360, width=250, thickness=18).model_dump(),
    }
}
