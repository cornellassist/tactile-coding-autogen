# Tactile Coding Blocks Generator

A web app that converts Quorum code into 3D-printable tactile braille coding blocks. Write Quorum code in the editor, click Generate, and download `.scad` / `.stl` files ready for OpenSCAD or a 3D printer.

---

## What each part does

| File / Folder | Purpose |
|---|---|
| `brailleGen/braillegen_gui.py` | Flask backend (port 5001). Handles `/translate_and_generate` and `/download` endpoints |
| `brailleGen/translate.py` | Translates text to braille via liblouis; parses Quorum code into Blockly XML |
| `brailleGen/gen.py` | Generates OpenSCAD geometry for braille dots, runs OpenSCAD to export `.stl` |
| `brailleGen/iv.py` | Input validation for braille parameters |
| `brailleGen/liblouis/tables/` | Braille translation table files (`.ctb`) used by the liblouis engine |
| `brailleGen/frontend/src/App.js` | Main React UI: CodeMirror editor, toolbar, Quorum block tray |
| `brailleGen/frontend/public/index.html` | Loads the Quorum block editor scripts |
| `brailleGen/frontend/public/quorum-website/` | Local copy of the Quorum language WebAssembly runtime and block editor |

---

## Prerequisites

### macOS

**1. Homebrew** (if not already installed)
```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

**2. liblouis** (braille translation library)
```bash
brew install liblouis
```

**3. OpenSCAD** (3D model generation)

Download and install from https://openscad.org/downloads.html, or:
```bash
brew install openscad
```

**4. Python 3** and **Node.js**
```bash
brew install python node
```

### Linux (Debian/Ubuntu)
```bash
apt-get install -y liblouis-dev liblouis-data
# Install Node.js via https://nodejs.org or nvm
```

---

## Setup

### 1. Clone the repo
```bash
git clone https://github.com/cornellassist/tactile-coding-autogen.git
cd tactile-coding-autogen
```

### 2. Install Python dependencies
```bash
cd brailleGen
pip install -r requirements.txt
```

### 3. Install frontend dependencies
```bash
cd brailleGen/frontend
npm install
```

### 4. Set up the Quorum block editor

The Quorum block editor runtime lives in `brailleGen/frontend/public/quorum-website/`. This folder contains two parts that need to be sourced separately:

**Part A — QuorumWebsite** (the compiled WebAssembly runtime):

Clone the Quorum website repo into the folder:
```bash
cd brailleGen/frontend/public/quorum-website
git clone https://github.com/qorf/quorum-website.git QuorumWebsite
```

The app expects these files to exist:
- `quorum-website/QuorumWebsite/Run/load.js`
- `quorum-website/QuorumWebsite/Run/load.data`
- `quorum-website/QuorumWebsite/Run/load.wasm`
- `quorum-website/QuorumWebsite/Run/QuorumStandardLibrary.js`
- `quorum-website/QuorumWebsite/html/script/blockEditor.js`
- `quorum-website/QuorumWebsite/html/script/script.js`
- `quorum-website/QuorumWebsite/html/script/jquery-1.8.3.min.js`

**Part B — WebBlockEditor** (the block editor source + compiled output):

Clone the Quorum WebBlockEditor repo:
```bash
cd brailleGen/frontend/public/quorum-website
git clone https://github.com/qorf/WebBlockEditor.git WebBlockEditor
```

To rebuild `blockEditor.js` from source after any changes:
```bash
cd brailleGen/frontend/public/quorum-website/WebBlockEditor
bash copyToWeb.sh
```

> **Note:** If you already have the `quorum-website/` folder populated (e.g., cloned from this repo with submodules), you can skip Part A and Part B.

---

## Running

Start both servers in separate terminals.

### Terminal 1 — Backend (Flask)
```bash
cd brailleGen
python3 braillegen_gui.py
```
Runs at `http://localhost:5001`

### Terminal 2 — Frontend (React)
```bash
cd brailleGen/frontend
npm start
```
Opens at `http://localhost:3000`

---

## Using the app

1. Type Quorum code in the **left editor**. Supported commands:
   ```
   say "text"
   action Main
   class Main
   end
   ```
2. Select a braille table (e.g. `en-us-g2.ctb` for Grade 2 English).
3. Click **Generate** — the backend translates the code to braille and runs OpenSCAD to produce `.scad` and `.stl` files.
4. Click **Download SCAD** or **Download STL** to save the files.

The **right panel** is the Quorum Hour of Code block editor tray (interactive drag-and-drop block coding).

---

## Notes

- OpenSCAD must be installed for `.stl` generation. The app checks these paths in order:
  - `/Applications/OpenSCAD/OpenSCAD.app/Contents/MacOS/OpenSCAD`
  - `/Applications/OpenSCAD-2021.01.app/Contents/MacOS/OpenSCAD`
  - `openscad` on your `PATH`
- On macOS, `liblouis.20.dylib` is loaded automatically from `/opt/homebrew/lib/` — no need to set `DYLD_LIBRARY_PATH`.
