import os
from flask import Flask, request, send_file, render_template

app = Flask(__name__)

UPLOAD_FOLDER = './static/photos'
GCODE_FOLDER = './'

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(GCODE_FOLDER, exist_ok=True)

@app.route('/')
def index():
    return render_template('simple.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return "No file part", 400
    file = request.files['file']
    if file.filename == '':
        return "No selected file", 400

    # Save the uploaded file
    filepath = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(filepath)

    # Generate G-code using Inkscape CLI
    output_gcode = os.path.join(GCODE_FOLDER, f"{os.path.splitext(file.filename)[0]}.gcode")
    inkscape_command = f"inkscape {filepath} --actions='org.inkscape.extension.gcode_tools.path_to_gcode;file-save;file-close' -o {output_gcode}"
    os.system(inkscape_command)

    # Modify the G-code for specific pen-up/pen-down commands
    modify_gcode(output_gcode, pen_up="G00 Z0", pen_down="G00 Z3.5")

    return send_file(output_gcode, as_attachment=True)

def modify_gcode(gcode_path, pen_up, pen_down):
    with open(gcode_path, 'r') as file:
        lines = file.readlines()
    with open(gcode_path, 'w') as file:
        for line in lines:
            # Replace placeholder commands with specific parameters
            if "M03" in line:  # Assuming M03 means pen down
                file.write(f"{pen_down}\n")
            elif "M05" in line:  # Assuming M05 means pen up
                file.write(f"{pen_up}\n")
            else:
                file.write(line)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
