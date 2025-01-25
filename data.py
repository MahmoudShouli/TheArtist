gcode_commands_black = [
    "G10 L20 P1 X0 Y0 Z0",  # Set current position as origin
    "G90",
    "M3 S150",                 
    "G00 Y39",              # Move to Y39
    "G00 X300",             # Move to X300
    "G00 Z4.5",             # Move to Z4.5
    "G00 X308",             # Move to X308
    "M3 S0",                # Turn spindle off
    "G00 Z0",               # Move Z to 0
    "G00 X0 Y0"             # Move back to origin
]

    # Array of G-code commands to send
gcode_commands_blue = [
    "G10 L20 P1 X0 Y0 Z0",  # Set current position as origin
    "G90",                  # Set absolute positioning
    "M3 S150", 
    "G00 Y68",              # Move to Y39
    "G00 X300",             # Move to X300
    "G00 Z4.5",             # Move to Z4.5
    "G00 X308",             # Move to X308
    "M3 S0",                # Turn spindle off
    "G00 Z0",               # Move Z to 0
    "G00 X0 Y0"             # Move back to origin
]

gcode_drawing = [
    
    "G00 X100 Y100",
    "G00 X0 Y0"
   
]

gcode_retrieve_black = []

gcode_retrieve_blue = []


