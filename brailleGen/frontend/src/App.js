import React, { useState, useEffect, useRef } from "react";
import axios from "axios";
import * as Blockly from "blockly";
import { javascriptGenerator } from "blockly/javascript";
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

  const defineBlocks = () => {
    if (Blockly.Blocks['quorum_statement'] || Blockly.Blocks['output']) {
      console.log("Blocks are already defined.");
      return;
    }
    console.log("Defining blocks...");
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
      },
      {
        type: "comment",
        message0: "// %1",
        args0: [{ type: "field_input", name: "TEXT", text: "" }],
        previousStatement: null,
        nextStatement: null,
        colour: 60,
        tooltip: "Comment"
      }
      // For variables, math, loops, if → Blockly already has built-in blocks
    ]);
  };

  // --- Initialize Blockly workspace
  useEffect(() => {
    // Define blocks before initializing Blockly
    defineBlocks();

    if (!workspaceRef.current) {
      let toolboxXml = document.getElementById("toolbox");

      // If toolbox is not available, create a default toolbox XML
      if (!toolboxXml) {
        const defaultToolboxXml = `
        <xml xmlns="https://developers.google.com/blockly/xml">
  <block type="controls_if">
    <value name="IF0">
      <block type="logic_boolean">
        <field name="BOOL">TRUE</field>
      </block>
    </value>
    <statement name="DO0">
      <block type="output">
        <field name="TEXT">hi</field>
        <next>
          <block type="output">
            <field name="TEXT">world</field>
          </block>
        </next>
      </block>
    </statement>
    <next>
      <block type="output">
        <field name="TEXT">done</field>
      </block>
    </next>
  </block>
</xml>


      `;
        // Create a new DOM element to inject the default toolbox
        const toolboxDom = Blockly.utils.xml.textToDom(defaultToolboxXml);
        toolboxXml = toolboxDom;
      }

      // Now inject Blockly workspace
      workspaceRef.current = Blockly.inject("blocklyDiv", {
        toolbox: toolboxXml,
        trashcan: true,
        scrollbars: true,
        renderer: "thrasos",
      });

      reloadPalette()
    }

    // Handle window resize to resize Blockly workspace
    const onResize = () => {
      if (workspaceRef.current) {
        Blockly.svgResize(workspaceRef.current);
      }
    };

    window.addEventListener("resize", onResize);

    // Cleanup resize listener on component unmount
    return () => {
      window.removeEventListener("resize", onResize);
    };
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
      const res = await fetch(`/WebBlockEditor/palette.xml?ts=${Date.now()}`);
      if (!res.ok) throw new Error("palette.xml not found");

      const xmlText = await res.text();
      const xmlDom = Blockly.utils.xml.textToDom(xmlText);

      // Ensure the toolbox structure has categories
      if (!xmlDom.querySelector("category")) {
        console.warn("Toolbox XML does not contain categories. Adding default category.");

        const defaultCategoryXml = `
        <category name="Quorum Blocks" colour="#5C81A6">
          <block type="quorum_statement">
            <field name="CODE">// Write your Quorum code here</field>
          </block>
          <block type="output">
            <field name="TEXT">hi</field>
          </block>
        </category>
      `;

        const defaultCategoryDom = Blockly.utils.xml.textToDom(defaultCategoryXml);
        xmlDom.appendChild(defaultCategoryDom);
      }

      // Update the toolbox with the new XML structure
      if (workspaceRef.current) {
        workspaceRef.current.updateToolbox(xmlDom);
      }

    } catch (err) {
      console.warn("Failed to load palette.xml, toolbox unchanged", err);
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
      <div
        id="toolbox"
        style={{ display: "none" }}
        dangerouslySetInnerHTML={{
          __html: `<xml xmlns="https://developers.google.com/blockly/xml">
      <category name="Logic" categorystyle="logic_category"></category>
      <category name="Loops" categorystyle="loop_category"></category>
      <category name="Math" categorystyle="math_category"></category>
      <category name="Text" categorystyle="text_category"></category>
      <category name="Lists" categorystyle="list_category"></category>
      <category name="Variables" categorystyle="variable_category"></category>
      <category name="Functions" categorystyle="procedure_category"></category>
      <sep></sep>
      <category name="Quorum Custom" colour="#5C81A6">
        <block type="output"></block>
        <block type="quorum_statement"></block>
        <block type="comment"></block>
      </category>
    </xml>` }}
      />
      <div style={{ height: "100vh", display: "flex", flexDirection: "column" }}>
        {/* Header */}
        <div
          style={{
            backgroundColor: "#FFE4C9",
            color: "#111",
            padding: "12px 16px",
            fontSize: 20,
            fontWeight: "bold",
            borderBottom: "1px solid #ddd",
          }}
        >
          Braille Tile Generator
        </div>

        {/* Controls */}
        <div
          style={{
            display: "flex",
            alignItems: "center",
            gap: 12,
            backgroundColor: "#E78895",
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
          <button
            onClick={async () => {
              try {
                const code = cmView.current
                  ? cmView.current.state.doc.toString()
                  : "";
                const response = await axios.post("http://localhost:5001/run", { code });
                console.log("Run output:", response.data);
                alert("Program output:\n" + response.data.output);
              } catch (err) {
                console.error("Run error:", err);
                alert("Failed to run program");
              }
            }}
            style={{ padding: "8px 12px", fontWeight: 600 }}
          >
            Run
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

          {/* Right: Blockly workspace */}
          <div
            style={{
              flex: 1,
              padding: 20,
              display: "flex",
              flexDirection: "column",
              minHeight: 0,
            }}
          >
            <label>
              <strong>Workspace</strong>
            </label>
            <div
              id="blocklyDiv"
              style={{
                flex: 1,
                minHeight: 240,
                border: "1px solid #ddd",
                borderRadius: 8,
                marginTop: 8,
                boxSizing: "border-box",
              }}
            />
          </div>
        </div>
      </div>
    </>
  );
}

export default App;
