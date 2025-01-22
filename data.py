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

drawing_gcode = [
    "G00 F1800.0 Y0.000; !!Ybottom",
    "G00 F1800.0 X0.000; !!Xleft",
    "G00 F1800.0 X55.855 Y145.009; move !!Xleft+55.855 Ybottom+145.009",
    "G00 Z2.4",
    "G01 F1200.0 X55.915 Y147.407; draw !!Xleft+55.915 Ybottom+147.407",
    "G01 F1200.0 X56.092 Y149.799; draw !!Xleft+56.092 Ybottom+149.799",
    "G01 F1200.0 X56.387 Y152.180; draw !!Xleft+56.387 Ybottom+152.180",
    "G01 F1200.0 X56.800 Y154.544; draw !!Xleft+56.800 Ybottom+154.544",
    "G01 F1200.0 X57.328 Y156.884; draw !!Xleft+57.328 Ybottom+156.884",
    "G01 F1200.0 X57.971 Y159.196; draw !!Xleft+57.971 Ybottom+159.196",
    "G01 F1200.0 X58.728 Y161.474; draw !!Xleft+58.728 Ybottom+161.474",
    "G01 F1200.0 X59.596 Y163.712; draw !!Xleft+59.596 Ybottom+163.712",
    "G01 F1200.0 X60.573 Y165.905; draw !!Xleft+60.573 Ybottom+165.905",
    "G01 F1200.0 X61.658 Y168.048; draw !!Xleft+61.658 Ybottom+168.048",
    "G01 F1200.0 X62.847 Y170.135; draw !!Xleft+62.847 Ybottom+170.135",
    "G01 F1200.0 X64.137 Y172.162; draw !!Xleft+64.137 Ybottom+172.162",
    "G01 F1200.0 X65.526 Y174.123; draw !!Xleft+65.526 Ybottom+174.123",
    "G01 F1200.0 X67.010 Y176.014; draw !!Xleft+67.010 Ybottom+176.014",
    "G01 F1200.0 X68.586 Y177.830; draw !!Xleft+68.586 Ybottom+177.830",
    "G01 F1200.0 X70.249 Y179.568; draw !!Xleft+70.249 Ybottom+179.568",
    "G01 F1200.0 X71.996 Y181.222; draw !!Xleft+71.996 Ybottom+181.222",
    "G01 F1200.0 X73.822 Y182.789; draw !!Xleft+73.822 Ybottom+182.789",
    "G01 F1200.0 X75.723 Y184.265; draw !!Xleft+75.723 Ybottom+184.265",
    "G01 F1200.0 X77.695 Y185.646; draw !!Xleft+77.695 Ybottom+185.646",
    "G01 F1200.0 X79.733 Y186.929; draw !!Xleft+79.733 Ybottom+186.929",
    "G01 F1200.0 X81.832 Y188.112; draw !!Xleft+81.832 Ybottom+188.112",
    "G01 F1200.0 X83.986 Y189.190; draw !!Xleft+83.986 Ybottom+189.190",
    "G01 F1200.0 X86.191 Y190.162; draw !!Xleft+86.191 Ybottom+190.162",
    "G01 F1200.0 X88.442 Y191.026; draw !!Xleft+88.442 Ybottom+191.026",
    "G01 F1200.0 X90.732 Y191.778; draw !!Xleft+90.732 Ybottom+191.778",
    "G01 F1200.0 X93.057 Y192.418; draw !!Xleft+93.057 Ybottom+192.418",
    "G01 F1200.0 X95.410 Y192.943; draw !!Xleft+95.410 Ybottom+192.943",
    "G01 F1200.0 X97.787 Y193.353; draw !!Xleft+97.787 Ybottom+193.353",
    "G01 F1200.0 X100.181 Y193.647; draw !!Xleft+100.181 Ybottom+193.647",
    "G01 F1200.0 X102.586 Y193.824; draw !!Xleft+102.586 Ybottom+193.824",
    "G01 F1200.0 X104.997 Y193.882; draw !!Xleft+104.997 Ybottom+193.882",
    "G00 Z0"
]
