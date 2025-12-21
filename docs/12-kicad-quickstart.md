# Circuit Design Workflow: SKiDL + KiCad

This project uses **SKiDL** for circuit definition (schematic capture) and **KiCad** for PCB layout.

## Why SKiDL?

- **Pure Python**: Circuits defined as code, not GUI operations
- **Version control friendly**: Clean diffs, no binary files
- **ERC built-in**: Electrical rules checking happens at build time
- **Reproducible**: Run the script, get the same netlist every time

## Project Structure

```
euroscope/
├── circuits/               # SKiDL circuit definitions
│   ├── __init__.py         # Shared config (KiCad paths, etc.)
│   ├── build.py            # Build script for all circuits
│   └── power_supply.py     # Power supply circuit
├── kicad/
│   └── trace-eurorack-module/
│       ├── netlists/       # Generated netlists (from SKiDL)
│       ├── *.kicad_pcb     # PCB layout (manual in KiCad)
│       └── *.kicad_pro     # KiCad project file
├── .venv/                  # Python virtual environment
└── requirements.txt        # Python dependencies
```

## Setup

### 1. Create Virtual Environment

```bash
cd /Users/navicore/git/navicore/euroscope
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2. Verify KiCad Installation

SKiDL requires KiCad libraries. The default path on macOS is:
```
/Applications/KiCad/KiCad.app/Contents/SharedSupport/symbols
```

This is configured in `circuits/__init__.py`.

## Building Circuits

### Build All Circuits

```bash
source .venv/bin/activate
python circuits/build.py
```

This runs ERC on each circuit and generates netlists to `kicad/trace-eurorack-module/netlists/`.

### Build Single Circuit

```bash
source .venv/bin/activate
python circuits/power_supply.py
```

## Writing Circuit Definitions

### Basic Structure

```python
#!/usr/bin/env python3
"""Circuit description."""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from circuits import init_skidl, OUTPUT_DIR

init_skidl()

from skidl import *

# Define nets
vcc = Net('+5V')
gnd = Net('GND')
vcc.drive = POWER  # Tell ERC this is a power source
gnd.drive = POWER

# Define components
r1 = Part('Device', 'R', value='10k',
          footprint='Resistor_SMD:R_0805_2012Metric')

# Make connections
vcc += r1[1]
gnd += r1[2]

# Run ERC and generate netlist
ERC()
netlist_path = OUTPUT_DIR / 'my_circuit.net'
generate_netlist(file_=str(netlist_path))
```

### Key Concepts

#### Parts
```python
# Basic part
r1 = Part('Device', 'R', value='10k',
          footprint='Resistor_SMD:R_0805_2012Metric')

# Access pins by number
r1[1]  # Pin 1
r1[2]  # Pin 2

# Access pins by name (for ICs)
u1 = Part('Regulator_Switching', 'AP63203WU', ...)
u1['IN']   # Input pin
u1['GND']  # Ground pin
u1['SW']   # Switch node
```

#### Nets
```python
# Create named nets
vcc = Net('+5V')
gnd = Net('GND')
signal = Net('SIG')

# Mark power nets (for ERC)
vcc.drive = POWER

# Connect pins to nets
vcc += r1[1], c1[1]  # Multiple pins to one net
r1[2] += signal      # Single connection
```

#### Connections
```python
# Connect multiple things to a net
gnd += j1[2], j1[3], j1[4], c1[2], u1['GND']

# Chain connections
r1[2] += signal, r2[1]  # r1 pin 2 and r2 pin 1 share 'signal' net
```

### Finding Parts

Parts come from KiCad's symbol libraries. Common libraries:

| Library | Contents |
|---------|----------|
| `Device` | R, C, L, LED, D, D_Schottky |
| `Connector_Generic` | Conn_01x02, Conn_02x05_Odd_Even |
| `Regulator_Switching` | Buck/boost regulators |
| `Amplifier_Operational` | TL074, LM358, etc. |
| `power` | +12V, GND, +3.3V symbols |

Browse libraries in KiCad's Symbol Editor, or check:
```
/Applications/KiCad/KiCad.app/Contents/SharedSupport/symbols/
```

### Finding Footprints

Common footprints:

| Component | Footprint |
|-----------|-----------|
| 0805 resistor | `Resistor_SMD:R_0805_2012Metric` |
| 0805 capacitor | `Capacitor_SMD:C_0805_2012Metric` |
| SMA diode | `Diode_SMD:D_SMA` |
| TSOT-23-6 | `Package_TO_SOT_SMD:TSOT-23-6` |
| 2x5 IDC header | `Connector_IDC:IDC-Header_2x05_P2.54mm_Vertical` |

## PCB Layout Workflow

After generating netlists:

1. **Open KiCad project**: `kicad/trace-eurorack-module/trace-eurorack-module.kicad_pro`

2. **Open PCB editor** (Pcbnew)

3. **Import netlist**: File → Import → Netlist
   - Select: `kicad/trace-eurorack-module/netlists/power_supply.net`
   - Click "Update PCB"

4. **Place components**: Arrange on board

5. **Route traces**: Connect pads per netlist

6. **Run DRC**: Design Rules Check

7. **Generate Gerbers**: For PCB fabrication

## Current Circuits

### power_supply.py

Converts Eurorack +12V to +3.3V for the RP2040.

**Components:**
- J1: 2x5 Eurorack power connector
- D1: SS14 Schottky (reverse polarity protection)
- U1: AP63203WU-7 buck regulator
- C1: 10µF input capacitor
- C2: 22µF output capacitor
- C3: 100nF bootstrap capacitor
- L1: 10µH inductor

**Nets:**
- +12V: From Eurorack power
- GND: Common ground
- +3.3V: Regulated output
- -12V: Protected (diode blocks reverse polarity)
- SW: Buck regulator switch node

## Adding New Circuits

1. Create `circuits/new_circuit.py` following the template above
2. Add to `CIRCUITS` list in `circuits/build.py`
3. Run `python circuits/build.py`
4. Import netlist into KiCad PCB

## Troubleshooting

### "No module named 'circuits'"
Make sure you're running from the project root:
```bash
cd /Users/navicore/git/navicore/euroscope
python circuits/power_supply.py
```

### ERC Warnings: "Insufficient drive current"
Add power flags to power nets:
```python
vcc = Net('+5V')
vcc.drive = POWER
```

### ERC Warnings: "Only one pin attached to net"
Normal for unused nets (like -12V protection). Can be ignored if intentional.

### "KICAD8_SYMBOL_DIR environment variable is missing"
The `init_skidl()` function sets this. Make sure to call it before importing from skidl:
```python
from circuits import init_skidl, OUTPUT_DIR
init_skidl()
from skidl import *
```

## Resources

- [SKiDL Documentation](https://devbisme.github.io/skidl/)
- [SKiDL GitHub](https://github.com/devbisme/skidl)
- [KiCad Documentation](https://docs.kicad.org/)
- Project design docs: `docs/11-schematic-design-plan.md`
