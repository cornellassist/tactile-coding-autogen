import React, { useState, useEffect, useRef } from "react";
import axios from "axios";
import { EditorView, basicSetup } from "codemirror";
import { EditorState } from "@codemirror/state";
import { javascript } from "@codemirror/lang-javascript";
import { indentWithTab } from "@codemirror/commands";
import { keymap } from "@codemirror/view";

function App() {
  const cmView = useRef(null);
  const iframeRef = useRef(null);
  const [selectedTable, setSelectedTable] = useState("en-us-g2.ctb");
  const [params, setParams] = useState({ length: "", depth: "", lineSpacing: "" });
  const [slabMode, setSlabMode] = useState(false);
  const [lastScadFile, setLastScadFile] = useState(null);
  const [lastStlFile, setLastStlFile] = useState(null);

  useEffect(() => {
    function handleMessage(event) {
      const { type, code } = event.data;

      if (type === "BLOCK_EDITOR_READY") {
        console.log("Quorum iframe is ready.");
      }

      if (type === "BLOCK_CODE_CHANGED" && cmView.current) {
        const current = cmView.current.state.doc.toString();
        if (current !== code) {
          cmView.current.dispatch({
            changes: { from: 0, to: current.length, insert: code }
          });
        }
      }
    }

    window.addEventListener("message", handleMessage);
    return () => window.removeEventListener("message", handleMessage);
  }, []);

  useEffect(() => {
    if (!cmView.current) {
      const parent = document.getElementById("QuorumEditor");
      if (parent) {
        const state = EditorState.create({
          doc: "// Write your Quorum code here\n",
          extensions: [
            basicSetup,
            javascript(),
            keymap.of([indentWithTab]),
            EditorView.updateListener.of((update) => {
              if (update.docChanged && window.QUORUM_EDITOR) {
                const code = update.state.doc.toString();
                window.QUORUM_EDITOR.SetCode$quorum_text(code);
              }
            })
          ]
        });
        cmView.current = new EditorView({ state, parent });
      }
    }
  }, []); // --- Initialize Quorum editor (blockEditor.js) + CodeMirror

  const workspaceRef = useRef(null);

  // --- Handle translation
  const handleTranslate = async () => {
    try {
      let code = "";
      if (cmView.current) code = cmView.current.state.doc.toString();
      const timeStamp = new Date().toISOString().replace(/[^\w\s]/gi, "_");

      const response = await axios.post("http://localhost:5001/translate_and_generate", {
        code,
        params: { table: selectedTable, file_name: timeStamp },
        language: "quorum",
      });

      setLastScadFile(response.data.scad_file);
      setLastStlFile(response.data.stl_file);
      alert(response.data.message); // let the user know files were generated
    } catch (error) {
      console.error("Failed to generate files:", error);
    }
  };

  const handleParamChange = (e) => {
    const { name, value } = e.target;
    setParams((prev) => ({ ...prev, [name]: value }));
  };

  const handleTableChange = (e) => setSelectedTable(e.target.value);

  return (
    <>
      <div style={{ height: "100vh", display: "flex", flexDirection: "column" }}>
        {/* Header */}
        <div
          style={{
            backgroundColor: "#8D2018",
            color: "#DEBEBC",
            padding: "12px 16px",
            fontSize: 40,
            fontWeight: "bold",
            borderBottom: "1px solid #ddd",
            display: "flex",
            alignItems: "center",
            justifyContent: "space-between",
          }}
        >
          <span>Tactile Coding Blocks Generator</span>
          <img src="/cat_logo2.png" alt="Logo" style={{ height: "150px" }} />
        </div>

        {/* Controls */}
        <div
          style={{
            display: "flex",
            alignItems: "center",
            gap: 12,
            backgroundColor: "#DEBEBC",
            padding: "10px 16px",
            flexWrap: "wrap",
            borderBottom: "1px solid #c7717e",
          }}
        >
          <button onClick={handleTranslate} style={{ padding: "8px 12px", fontWeight: 600 }}>
            Generate
          </button>
          <button
            onClick={() => {
              const link = document.createElement("a");
              link.href = `http://localhost:5001/download/${lastScadFile}`;
              link.click();
            }}
            disabled={!lastScadFile}
            style={{ padding: "8px 12px", fontWeight: 600 }}
          >
            Download SCAD
          </button>

          <button
            onClick={() => {
              const link = document.createElement("a");
              link.href = `http://localhost:5001/download/${lastStlFile}`;
              link.click();
            }}
            disabled={!lastStlFile}
            style={{ padding: "8px 12px", fontWeight: 600 }}
          >
            Download STL
          </button>

          <button
            onClick={() => {
              if (window.QUORUM_EDITOR) {
                window.QUORUM_EDITOR.SetCode$quorum_text("");
              }
              if (cmView.current) {
                cmView.current.dispatch({
                  changes: { from: 0, to: cmView.current.state.doc.length, insert: "" },
                });
              }
            }}
            style={{ padding: "8px 12px" }}
          >
            Clear Code
          </button>
          <button
            onClick={() => window.QUORUM_EDITOR && window.QUORUM_EDITOR.Clear$()}
            style={{ padding: "8px 12px" }}
          >
            Clear Blocks
          </button>
          <div style={{ display: "flex", alignItems: "center", gap: 6 }}>
            <label>Braille Table:</label>
            <select value={selectedTable} onChange={handleTableChange}>
              <option value="en-us-g2.ctb">en-us-g2.ctb</option>
              <option value="en-us-g1.ctb">en-us-g1.ctb</option>
            </select>
          </div>

          <div style={{ display: "flex", alignItems: "center", gap: 6 }}>
            <label>Slab</label>
            <input type="checkbox" checked={slabMode} onChange={(e) => setSlabMode(e.target.checked)} />
          </div>

          <div style={{ display: "flex", alignItems: "center", gap: 8, marginLeft: "auto" }}>
            <span>Braille Parameters:</span>
            <input
              type="number"
              name="length"
              value={params.length}
              onChange={handleParamChange}
              placeholder="length (mm)"
            />
            <input
              type="number"
              name="depth"
              value={params.depth}
              onChange={handleParamChange}
              placeholder="depth (mm)"
            />
            <input
              type="number"
              name="lineSpacing"
              value={params.lineSpacing}
              onChange={handleParamChange}
              placeholder="line spacing (mm)"
            />
          </div>
        </div>

        {/* Main split */}
        <div style={{ display: "flex", flex: 1, minHeight: 0 }}>
          {/* Left: Quorum editor (CodeMirror injected + synced with blockEditor.js) */}
          <div
            style={{
              flex: 1,
              padding: 20,
              borderRight: "1px solid #000",
              display: "flex",
              flexDirection: "column",
              minHeight: 0,
            }}
          >
            <label>
              <strong>Quorum IDE</strong>
            </label>
            <div
              id="QuorumEditor"
              style={{
                flex: 1,
                border: "1px solid #ddd",
                borderRadius: 8,
                marginTop: 8,
                fontFamily: "monospace",
                fontSize: 14,
                lineHeight: "1.4",
                overflow: "auto",
                background: "#fafafa",
              }}
            />
          </div>
          {/* Right: Quorum block workspace */}
          <div style={{ flex: 1, padding: 20, display: "flex", flexDirection: "column" }}>
            <label><strong>Workspace</strong></label>
          </div>
        </div>
      </div >
    </>
  );
}

export default App;
