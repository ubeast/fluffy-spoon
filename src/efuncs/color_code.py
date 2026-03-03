"""Provides a standardized, immutable library of colors for use across the application.

This module defines and builds a hierarchical color standard object that can be
easily imported and used. It is designed to be read-only to ensure color consistency.

Sample Usage:
    from cfuncs.color_standards import color_standard

    army_green_hex = color_standard.branch.army.hex
    marines_red_rgb = color_standard.branch.marines.rgb
    performance_yellow_hsl = color_standard.performance.yellow.hsl
    print(f"The hex code for the Army color is: {army_green_hex}")
"""
from dataclasses import dataclass, make_dataclass
from typing import Any


@dataclass(frozen=True)
class Color:
    hex: str
    rgb: tuple[int, int, int]   # Fixed-length, immutable — more appropriate than list
    hsl: tuple[int, int, int]


# fmt: off
COLOR_DATA: list[tuple] = [
    # Category,       Name,               Hex,       RGB,                HSL
    ('performance', 'green',          '#008000', (  0, 128,   0), (120, 100, 25)),
    ('performance', 'yellow',         '#FFFF00', (255, 255,   0), ( 60, 100, 50)),
    ('performance', 'red',            '#FF0000', (255,   0,   0), (  0, 100, 50)),
    ('performance', 'black',          '#000000', (  0,   0,   0), (  0,   0,  0)),
    ('performance', 'low_visibility', '#A020F0', (160,  32, 240), (277,  87, 53)),
    ('segment',     'source',         '#A52A2A', (165,  42,  42), (  0,  59, 41)),
    ('segment',     'supplier',       '#808080', (128, 128, 128), (  0,   0, 50)),
    ('segment',     'transporter',    '#0072BB', (  0, 114, 187), (203, 100, 37)),
    ('segment',     'theater',        '#4B5320', ( 75,  83,  32), ( 69,  44, 23)),
    ('branch',      'army',           '#4B5320', ( 75,  83,  32), ( 69,  44, 23)),
    ('branch',      'air_force',      '#5D8AA8', ( 93, 138, 168), (204,  29, 51)),
    ('branch',      'navy',           '#000080', (  0,   0, 128), (240, 100, 25)),
    ('branch',      'marines',        '#C41E3A', (196,  30,  58), (350,  74, 44)),
]
# fmt: on


def build_color_library(data: list[tuple]) -> Any:
    """
    Dynamically builds a frozen, hierarchical dataclass from COLOR_DATA.
    Returns Any because the top-level class is created at runtime via make_dataclass.
    """
    # Group colors by category
    categories: dict[str, dict[str, Color]] = {}
    for category, name, hex_val, rgb_val, hsl_val in data:
        categories.setdefault(category, {})[name] = Color(
            hex=hex_val,
            rgb=rgb_val,
            hsl=hsl_val,
        )

    # Build a frozen dataclass for each category
    category_instances: dict[str, Any] = {}
    for category_name, colors in categories.items():
        CategoryClass = make_dataclass(
            cls_name=f'ColorCategory_{category_name.capitalize()}',  # Unique name avoids class collisions
            fields=[(name, Color) for name in colors],
            frozen=True,
        )
        category_instances[category_name] = CategoryClass(**colors)

    # Build the top-level library dataclass
    ColorLibrary = make_dataclass(
        cls_name='ColorLibrary',
        fields=[(name, type(instance)) for name, instance in category_instances.items()],
        frozen=True,
    )

    return ColorLibrary(**category_instances)


color_standard = build_color_library(COLOR_DATA)
