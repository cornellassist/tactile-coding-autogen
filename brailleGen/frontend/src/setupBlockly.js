// src/setupBlockly.js
import Blockly from 'blockly/core';
import 'blockly/blocks';
import 'blockly/javascript';

// Function to initialize Blockly
export function initBlockly(workspaceDivId) {
    // Define the toolbox XML with a Quorum block
    const toolbox = `
    <xml id="toolbox" style="display: none">
      <category name="Quorum">
        <block type="text"></block>
        <block type="math_number"></block>
      </category>
    </xml>
  `;

    // Inject Blockly into the div
    const workspace = Blockly.inject(workspaceDivId, {
        toolbox: toolbox,
        scrollbars: true,
        trashcan: true,
    });

    return workspace;
}