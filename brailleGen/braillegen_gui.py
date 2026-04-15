import os
import ctypes
import datetime
from threading import Thread

# On macOS, liblouis.20.dylib lives in Homebrew's prefix which is not on the
# default dlopen search path.  Pre-populate ctypes.cdll's cache under the
# short name that `louis` looks for, so the import succeeds without needing
# DYLD_LIBRARY_PATH to be set externally.
_homebrew_liblouis = '/opt/homebrew/lib/liblouis.20.dylib'
if os.path.exists(_homebrew_liblouis):
    ctypes.cdll.__dict__['liblouis.20.dylib'] = ctypes.CDLL(_homebrew_liblouis)

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

# Start Flask server in a separate thread
if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5001)
