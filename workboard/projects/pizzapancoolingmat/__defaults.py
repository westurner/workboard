# This file has been renamed to schemas.py. Please import from schemas.py instead.

"""
Centralized default props for all pizzapancoolingmat components.

This file is intended to be imported at the top level of each module that needs defaults.
Avoid importing from pizzapancoolingmat.py or other component modules here to prevent circular imports.
"""
from pydantic import BaseModel, Field, JsonValue

# UNIT_MM = {"unit": "mm"}
# UNIT_MM: dict[str, str] = {"unit": "mm"}
UNIT_MM: dict[str, JsonValue] = {"unit": "mm"}

class PanModel(BaseModel):
    diameter: int = Field(330, description="Diameter of the pizza pan in mm.", json_schema_extra=UNIT_MM)
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
        "pan": PanModel().model_dump(), # type: ignore
        "riser": RiserModel().model_dump(), # type: ignore
        "laptop": LaptopModel().model_dump(), # type: ignore
    }
}
