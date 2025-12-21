#!/usr/bin/env python3
"""
Trace Eurorack Module - Power Supply
SKiDL circuit definition

Converts Eurorack +12V to +3.3V using AP63203WU buck regulator.
Includes reverse polarity protection on -12V rail.
"""

import sys
from pathlib import Path

# Add project root to path for imports
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from circuits import init_skidl, OUTPUT_DIR

init_skidl()

from skidl import *  # SKiDL uses star import pattern

# =============================================================================
# Power Nets
# =============================================================================
plus_12v = Net('+12V')
minus_12v = Net('-12V')
gnd = Net('GND')
plus_3v3 = Net('+3.3V')
sw_node = Net('SW')  # Switching node between regulator and inductor

# Power flags to indicate power sources to ERC
plus_12v.drive = POWER
gnd.drive = POWER
minus_12v.drive = POWER
plus_3v3.drive = POWER

# =============================================================================
# Components
# =============================================================================

# Eurorack Power Connector (2x5 shrouded header)
# Pin 1 = -12V, Pins 3-8 = GND, Pins 9,10 = +12V
j1 = Part('Connector_Generic', 'Conn_02x05_Odd_Even',
          value='Eurorack_Power',
          footprint='Connector_IDC:IDC-Header_2x05_P2.54mm_Vertical')

# Schottky diode for reverse polarity protection on -12V
d1 = Part('Device', 'D_Schottky',
          value='SS14',
          footprint='Diode_SMD:D_SMA')

# Buck regulator - AP63203WU-7 (3.3V fixed output)
u1 = Part('Regulator_Switching', 'AP63203WU',
          value='AP63203WU-7',
          footprint='Package_TO_SOT_SMD:TSOT-23-6')

# Input capacitor (before regulator)
c1 = Part('Device', 'C',
          value='10uF',
          footprint='Capacitor_SMD:C_0805_2012Metric')

# Output capacitor (after regulator)
c2 = Part('Device', 'C',
          value='22uF',
          footprint='Capacitor_SMD:C_0805_2012Metric')

# Bootstrap capacitor
c3 = Part('Device', 'C',
          value='100nF',
          footprint='Capacitor_SMD:C_0402_1005Metric')

# Output inductor
l1 = Part('Device', 'L',
          value='10uH',
          footprint='Inductor_SMD:L_1210_3225Metric')

# =============================================================================
# Connections
# =============================================================================

# Eurorack power connector pinout:
# Pin 1 = -12V (directly, no diode needed if we're not using -12V)
# Pins 2,4,6,8 = GND (right column)
# Pins 3,5,7 = GND (left column, middle pins)
# Pin 9 = +12V (left column, bottom)
# Pin 10 = +12V (right column, bottom)

# -12V rail with reverse polarity protection
# Diode cathode to connector, anode to -12V net
j1[1] += d1['K']  # Connector pin 1 to diode cathode
d1['A'] += minus_12v  # Diode anode to -12V net (protected)

# +12V connections
plus_12v += j1[9], j1[10], c1[1], u1['IN'], u1['EN']

# GND connections (all ground pins from connector + component grounds)
gnd += j1[2], j1[3], j1[4], j1[5], j1[6], j1[7], j1[8]
gnd += c1[2], u1['GND'], c2[2]

# Buck regulator output stage
u1['SW'] += sw_node, c3[1], l1[1]  # SW connects to bootstrap cap and inductor
u1['BST'] += c3[2]  # Bootstrap pin to other side of bootstrap cap

# Output voltage rail
l1[2] += plus_3v3  # Inductor output
plus_3v3 += c2[1], u1['FB']  # Output cap and feedback

# =============================================================================
# ERC and Output
# =============================================================================

print("=" * 60)
print("Trace Eurorack Module - Power Supply")
print("=" * 60)

# Run electrical rules check
ERC()

print("\n" + "=" * 60)
print("Circuit Summary")
print("=" * 60)
print(f"Total Parts: {len(default_circuit.parts)}")
print(f"Total Nets: {len(default_circuit.nets)}")

print("\nParts List:")
for part in sorted(default_circuit.parts, key=lambda p: p.ref):
    print(f"  {part.ref}: {part.value} ({part.footprint})")

print("\nNet Connections:")
for net in sorted(default_circuit.nets, key=lambda n: n.name):
    if net.name and not net.name.startswith('N$'):  # Skip auto-named nets
        pins = [f"{p.part.ref}.{p.num}" for p in net.pins]
        print(f"  {net.name}: {', '.join(pins)}")

# Generate netlist
netlist_path = OUTPUT_DIR / 'power_supply.net'
print("\n" + "=" * 60)
print("Generating netlist...")
print("=" * 60)
generate_netlist(file_=str(netlist_path))
print(f"Netlist written to: {netlist_path}")
