import React, { useState, useEffect, useRef } from "react";
import axios from "axios";
import * as Blockly from "blockly";
import { EditorView, basicSetup } from "codemirror";
import { EditorState } from "@codemirror/state";
import { javascript } from "@codemirror/lang-javascript";
import { indentWithTab } from "@codemirror/commands";
import { keymap } from "@codemirror/view";

function App() {
  const workspaceRef = useRef(null);
  const cmView = useRef(null);

  const [selectedTable, setSelectedTable] = useState("en-us-g2.ctb");
  const [params, setParams] = useState({ length: "", depth: "", lineSpacing: "" });
  const [slabMode, setSlabMode] = useState(false);
  const [lastScadFile, setLastScadFile] = useState(null);
  const [lastStlFile, setLastStlFile] = useState(null);

  // Define all custom blocks at the very top, synchronously
  const defineBlocks = () => {
    if (Blockly.Blocks['quorum_statement']) return; // already defined

    Blockly.defineBlocksWithJsonArray([
      {
        type: "output",
        message0: "output %1",
        args0: [{ type: "field_input", name: "TEXT", text: "" }],
        previousStatement: null,
        nextStatement: null,
        colour: 160,
        tooltip: "Quorum output"
      },
      {
        type: "quorum_statement",
        message0: "statement %1",
        args0: [{ type: "field_input", name: "CODE", text: "" }],
        previousStatement: null,
        nextStatement: null,
        colour: 120,
        tooltip: "Generic Quorum statement"
      }
    ]);
  };

  // --- Initialize Blockly workspace
  useEffect(() => {
    defineBlocks(); // blocks must exist

    // Now you can safely update the toolbox
    reloadPalette();
  }, []);

  // --- Initialize Quorum editor (blockEditor.js) + CodeMirror
  useEffect(() => {
    if (window.plugins_quorum_WebEditor_BlockEditor_) {
      window.QUORUM_EDITOR = new window.plugins_quorum_WebEditor_BlockEditor_();
      console.log("QUORUM_EDITOR initialized");

      defineBlocks(); // <- Re-define custom blocks AFTER blockEditor.js initializes
    }
    console.log("Blockly.Blocks available:", Object.keys(Blockly.Blocks));
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
            }),
          ],
        });
        cmView.current = new EditorView({ state, parent });
      }
    }
  }, []);

  // --- Reload toolbox from palette.xml
  const reloadPalette = async () => {
    try {
      // Fetch palette.xml
      const res = await fetch(`/quorum-website/WebBlockEditor/palette.xml?ts=${Date.now()}`);
      if (!res.ok) throw new Error("palette.xml not found");

      const xmlText = await res.text();
      const parser = new DOMParser();
      const paletteDom = parser.parseFromString(xmlText, "text/xml");

      // Find the "HoC" page
      const pages = Array.from(paletteDom.getElementsByTagName("page"));
      const hocPage = pages.find(p => p.getAttribute("name")?.trim() === "HoC");
      if (!hocPage) throw new Error("No HoC page found in palette.xml");

      // Build blocks XML
      let blocksXml = "";
      hocPage.querySelectorAll("block").forEach(b => {
        const codeSnippet = b.textContent.trim();
        let blockType = codeSnippet.startsWith("output") ? "output" : "quorum_statement";

        // Determine correct field name
        const fieldName = blockType === "output" ? "TEXT" : "CODE";

        // Insert block into toolbox
        blocksXml += `<block type="${blockType}"><field name="${fieldName}">${codeSnippet}</field></block>`;
      });

      // Build toolbox XML
      const toolboxXml = `
      <xml xmlns="https://developers.google.com/blockly/xml">
        <category name="Hour of Code" colour="#9C27B0">
          ${blocksXml}
        </category>
      </xml>
    `;

      // Parse and update Blockly toolbox
      const toolboxDom = Blockly.utils.xml.textToDom(toolboxXml);
      if (workspaceRef.current) {
        workspaceRef.current.updateToolbox(toolboxDom);
        console.log("Hour of Code tray loaded with", hocPage.querySelectorAll("block").length, "blocks!");
      }
    } catch (err) {
      console.error("Failed to load Hour of Code palette:", err);
    }
  };

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
            onClick={() => workspaceRef.current && workspaceRef.current.clear()}
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
        </div>
      </div>
    </>
  );
}

export default App;
