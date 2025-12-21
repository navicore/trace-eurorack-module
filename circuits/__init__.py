"""
Trace Eurorack Module - SKiDL Circuit Definitions

This package contains Python-based circuit definitions using SKiDL.
Running each module generates a KiCad-compatible netlist.
"""

import os
from pathlib import Path

# Project paths
PROJECT_ROOT = Path(__file__).parent.parent
OUTPUT_DIR = PROJECT_ROOT / 'kicad' / 'trace-eurorack-module' / 'netlists'

# KiCad library paths (macOS)
KICAD_SYMBOLS = "/Applications/KiCad/KiCad.app/Contents/SharedSupport/symbols"
KICAD_FOOTPRINTS = "/Applications/KiCad/KiCad.app/Contents/SharedSupport/footprints"


def init_skidl():
    """Initialize SKiDL with KiCad 8 library paths."""
    os.environ['KICAD8_SYMBOL_DIR'] = KICAD_SYMBOLS
    os.environ['KICAD8_FOOTPRINT_DIR'] = KICAD_FOOTPRINTS

    # Ensure output directory exists
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Import and configure skidl
    from skidl import set_default_tool, KICAD8
    set_default_tool(KICAD8)
