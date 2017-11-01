# BASTL Drill Tool

Inkscape extension to generate drilling gcode compatible with 3D printer firmwares. In the first place oriented to Repetier firmware.

Features:

* supports Repetier compatible g-code and Excellon format
* circles from drawing (up to specified diameter) are exported (no ellipses, arcs or paths are exported)
* rich options enable fine control of drilling process

Following options are available:

- **Output Format:**  type of output fiies - Excellon or g-code
- **Unit:**  units used in output file (mm or in).
- **Maximum Drill Diameter:** Maximum diameter of circle. Bigger circles will not be included in drill plan
- **Filename:** name of output file

Following options apply only to g-code output:

- **Spindle ON Command:**  command to turn on spindle (including speed specification)
- **Spindle OFF Command:**  command to turn off spindle
- **Tool Change Command:**  command to allow tool change
- **Additional initialization:**  additional initialization (in case we want keep default *Program Header*)
- **Message Command:**  command to display message on LCD display
- **Drill Height:**  height the holes will be drilled to (usually negative).
- **Safe Height:**  safe height to horizontally move the drill head
- **Tool Change Height:**  height on which can be tool changed
- **Drill Speed:** drill speed (Z axis)
- **Retract Speed:** retraction speed (Z axis)
- **Transport Speed:** move speed (X and Y axes) at safe height
- **Program Header:**  initialization sequence
- **Program Footer:**  termination sequence

If *Program Header* of *Program Footer* are left empty reasonable and safe defaults are used.

Multiline commands are supported. Vertical bar (|) can be used as command separator` it will be replaced by newline in output file.

