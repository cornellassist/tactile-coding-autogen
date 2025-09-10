import wx
import os
import sys
import datetime
import subprocess
from threading import Thread

# Import the translate and generate logic
from translate import louis_translate
from translate import quorum_to_blocks, louis_translate
from gen import generate_with_template
import iv  # Import the validation function from iv.py

# Flask app setup
from flask import send_from_directory, Flask, request, jsonify
from flask_cors import CORS

# Setup Flask app to handle translation requests
app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)

base_dir = os.path.dirname(os.path.abspath(__file__))
SCAD_FOLDER = os.path.join(base_dir, "scad_files")

@app.route('/download/<path:filename>', methods=['GET'])
def download_file(filename):
    try:
        return send_from_directory(SCAD_FOLDER, filename, as_attachment=True)
    except FileNotFoundError:
        return jsonify({"error": f"{filename} not found"}), 404
    
# --- Translate + Generate endpoint
@app.route('/translate_and_generate', methods=['POST', 'OPTIONS'])
def translate_and_generate():
    if request.method == "OPTIONS":
        return '', 200  # CORS preflight

    if not request.is_json:
        return jsonify({"error": "Content-Type must be application/json"}), 415

    data = request.get_json()
    code = data.get("code", "")
    params = data.get("params", {})
    language = data.get("language", "quorum")
    file_name = params.get("file_name")

    if not file_name:
        return jsonify({"error": "Missing file_name"}), 400

    # process each line separately
    for i, line in enumerate(code.splitlines(), start=1):
        line = line.strip()
        if not line:
            continue  # skip blank lines

        # first word = block type, rest = text
        parts = line.split(maxsplit=1)
        block_type = parts[0]
        block_text = parts[1] if len(parts) > 1 else ""
    try:
        braille_translation = louis_translate(block_type, params.get("table"), file_name)
    except Exception as e:
        return jsonify({"error": f"Translation failed: {str(e)}"}), 500

    # Then generate SCAD + STL
    try:
        generate_with_template(braille_translation, code, file_name)
    except Exception as e:
        return jsonify({"error": f"Failed to generate files: {str(e)}"}), 500

    return jsonify({
    "message": f"Generated {file_name}.scad and {file_name}.stl",
    "scad_file": f"{file_name}.scad",
    "stl_file": f"{file_name}.stl"
})

# --- Run endpoint
@app.route('/run', methods=['POST', 'OPTIONS'])
def run_code():
    if request.method == "OPTIONS":
        return '', 200

    if not request.is_json:
        return jsonify({"error": "Content-Type must be application/json"}), 415

    data = request.get_json()
    code = data.get("code", "")

    # Stub: just echo the code, later you can hook into an interpreter
    output_lines = []
    for line in code.splitlines():
        line = line.strip()
        if line.startswith("output"):
            msg = line[len("output"):].strip().strip('"')
            output_lines.append(msg)

    output = "\n".join(output_lines) if output_lines else f"Executed:\n{code}"
    return jsonify({"output": output})

# Run Flask app in a separate thread to avoid blocking wxPython GUI
def run_flask():
    app.run(debug=True, host='0.0.0.0', port=5001, use_reloader=False)  # Disabling the reloader to avoid signal issues on macOS

# wxPython GUI code
class main_window(wx.Frame):
    def __init__(self, *args, **kwds):
        # Initialize the GUI components
        kwds["style"] = kwds.get("style", 0) | wx.DEFAULT_FRAME_STYLE & ~wx.RESIZE_BORDER & ~wx.MAXIMIZE_BOX | wx.TAB_TRAVERSAL
        wx.Frame.__init__(self, *args, **kwds)
        self.SetSize((540, 720))
        self.SetTitle("Braille Tile Generator")
        self.SetBackgroundColour(wx.Colour(234, 234, 234))

        self.panel_1 = wx.Panel(self, wx.ID_ANY)

        # Add a button for generating the Braille tiles
        self.button_1 = wx.Button(self.panel_1, wx.ID_ANY, "Generate")
        self.button_1.Bind(wx.EVT_BUTTON, self.submit_clicked)  # Bind button click to the submit_clicked method

        # GUI components like text fields, labels, etc.
        # [Your GUI code for creating text fields, labels, and adding them to sizers]

    def submit_clicked(self, event):
        # Get input values from the GUI
        text_input = self.text_input.GetValue()
        cpl_input = self.cpl_input.GetValue()
        bh_input = self.bh_input.GetValue()
        ph_input = self.ph_input.GetValue()
        ms_input = self.ms_input.GetValue()
        es_input = self.es_input.GetValue()
        selected_table = self.braille_table_dropdown.GetValue()

        # Create a timestamp for the file name
        time_stamp = datetime.datetime.now().strftime("%H-%M-%S_%m-%d-%y")
        illegal_characters = '<>:"/\\|?*'
        file_name = time_stamp + "_" + ''.join(c for c in text_input[:8] if c not in illegal_characters)

        # Prepare the params to be passed to the translation function
        params = {
            'table': selected_table,
            'file_name': file_name,
            'length': cpl_input,
            'depth': bh_input,
            'lineSpacing': ms_input,
        }

        # Validate the user inputs before proceeding
        errors = iv.validate(text_input, "", cpl_input, bh_input, ph_input, ms_input, es_input)  # Pass empty string for translation to check only input values

        if errors:
            BrailleGen_statusbar_fields = ["Validation Errors: " + ", ".join(errors)]
            self.BrailleGen_statusbar.SetStatusText(BrailleGen_statusbar_fields[0], 0)

            # Show error message
            weewoo = wx.MessageDialog(self.panel_1, errors, "Following errors detected!", wx.OK | wx.ICON_EXCLAMATION | wx.CENTRE)
            weewoo.ShowModal()
            weewoo.Destroy()
            return  # Stop here if there are validation errors

        if selected_table == "quorum":
            translation = quorum_to_blocks(text_input)
        else:
            translation = louis_translate(text_input, selected_table, file_name)

        # Proceed to file generation
        BrailleGen_statusbar_fields = ["Generating!"]
        self.BrailleGen_statusbar.SetStatusText(BrailleGen_statusbar_fields[0], 0)

        # Call the generate function from gen.py to create Braille tiles
        generate_with_template(text_input, file_name)

        BrailleGen_statusbar_fields = ['Files saved to output files folder as "' + file_name + '"']
        self.BrailleGen_statusbar.SetStatusText(BrailleGen_statusbar_fields[0], 0)

        event.Skip()

# Start Flask server in a separate thread
if __name__ == '__main__':
    flask_thread = Thread(target=run_flask)
    flask_thread.start()

    # Run wxPython GUI
    BrailleGen = wx.App(False)
    frame = main_window(None, wx.ID_ANY, "")
    BrailleGen.MainLoop()
