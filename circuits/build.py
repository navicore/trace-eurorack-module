#!/usr/bin/env python3
"""
Build script for Trace Eurorack Module circuits.

Runs all circuit definitions and generates netlists.
"""

import subprocess
import sys
from pathlib import Path

CIRCUITS_DIR = Path(__file__).parent

# List of circuit modules to build
CIRCUITS = [
    'power_supply',
    # 'input_channel',   # TODO: implement
    # 'mcu_display',     # TODO: implement
    # 'user_controls',   # TODO: implement
]


def build_circuit(name: str) -> bool:
    """Build a single circuit, returns True on success."""
    module_path = CIRCUITS_DIR / f'{name}.py'
    if not module_path.exists():
        print(f"SKIP: {name}.py not found")
        return True

    print(f"\n{'='*60}")
    print(f"Building: {name}")
    print('='*60)

    result = subprocess.run(
        [sys.executable, str(module_path)],
        cwd=CIRCUITS_DIR.parent,  # Run from project root
    )

    if result.returncode != 0:
        print(f"FAILED: {name}")
        return False

    return True


def main():
    """Build all circuits."""
    print("Trace Eurorack Module - Circuit Build")
    print("="*60)

    success = True
    for circuit in CIRCUITS:
        if not build_circuit(circuit):
            success = False

    print("\n" + "="*60)
    if success:
        print("BUILD COMPLETE - All circuits generated successfully")
    else:
        print("BUILD FAILED - See errors above")
        sys.exit(1)


if __name__ == '__main__':
    main()
