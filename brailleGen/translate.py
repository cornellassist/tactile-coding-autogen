import os
import sys
import louis

# translate.py
from xml.etree.ElementTree import Element, SubElement, tostring

def quorum_to_blocks(code_input: str) -> str:
    """
    Convert Quorum-like code into Blockly XML.
    - Indentation-aware (nested blocks)
    - Single controls_if with elseif/else via mutation
    - Uses Blockly built-ins where possible
    """
    # ---------- helpers ----------
    def _indent_count(s: str) -> int:
        count = 0
        for ch in s:
            if ch == ' ':
                count += 1
            elif ch == '\t':
                count += 2
            else:
                break
        return count

    def _bool_block_from_text(text: str):
        b = Element("block", type="logic_boolean")
        f = SubElement(b, "field", name="BOOL")
        t = text.lower()
        f.text = "TRUE" if " true " in f" {t} " or t.endswith("true") or t.startswith("true") else "FALSE"
        return b

    def _chain(blocks):
        """Chain a list of <block> with <next> and return the head (or None)."""
        if not blocks:
            return None
        head = blocks[0]
        cur = head
        for b in blocks[1:]:
            nxt = SubElement(cur, "next")
            nxt.append(b)
            cur = b
        return head

    def _simple_block(text: str):
        # output "msg"
        if text.startswith("output"):
            blk = Element("block", type="output")
            fld = SubElement(blk, "field", name="TEXT")
            fld.text = text[len("output"):].strip().strip('"')
            return blk
        # say "msg"
        if text.startswith("say"):
            blk = Element("block", type="say")
            fld = SubElement(blk, "field", name="TEXT")
            fld.text = text[len("say"):].strip().strip('"')
            return blk
        # action "msg"
        if text.startswith("action"):
            blk = Element("block", type="action")
            fld = SubElement(blk, "field", name="TEXT")
            fld.text = text[len("action"):].strip().strip('"')
            return blk
        # integer x = 5 / number y = 2
        if text.startswith("integer") or text.startswith("number"):
            parts = text.split("=", 1)
            if len(parts) == 2:
                left = parts[0].strip().split()
                if len(left) >= 2:
                    var_name = left[1]
                    right_val = parts[1].strip()
                    blk = Element("block", type="variables_set")
                    fld = SubElement(blk, "field", name="VAR")
                    fld.text = var_name
                    val = SubElement(blk, "value", name="VALUE")
                    num = SubElement(val, "block", type="math_number")
                    nf = SubElement(num, "field", name="NUM")
                    nf.text = right_val if right_val.isdigit() else "0"
                    return blk
        # assignment x = 1 (very simple expr support)
        if "=" in text and not text.startswith("if") and not text.startswith("elseif"):
            var, expr = [p.strip() for p in text.split("=", 1)]
            blk = Element("block", type="variables_set")
            fld = SubElement(blk, "field", name="VAR")
            fld.text = var
            val = SubElement(blk, "value", name="VALUE")
            if "+" in expr:
                a, b = [p.strip() for p in expr.split("+", 1)]
                op = SubElement(val, "block", type="math_arithmetic")
                opf = SubElement(op, "field", name="OP")
                opf.text = "ADD"
                va = SubElement(op, "value", name="A")
                if a.isdigit():
                    nb = SubElement(va, "block", type="math_number")
                    nf = SubElement(nb, "field", name="NUM"); nf.text = a
                else:
                    vb = SubElement(va, "block", type="variables_get")
                    vf = SubElement(vb, "field", name="VAR"); vf.text = a
                vbv = SubElement(op, "value", name="B")
                if b.isdigit():
                    nb = SubElement(vbv, "block", type="math_number")
                    nf = SubElement(nb, "field", name="NUM"); nf.text = b
                else:
                    vb = SubElement(vbv, "block", type="variables_get")
                    vf = SubElement(vb, "field", name="VAR"); vf.text = b
            else:
                nb = SubElement(val, "block", type="math_number")
                nf = SubElement(nb, "field", name="NUM")
                nf.text = expr if expr.isdigit() else "0"
            return blk
        # comment
        if text.startswith("//"):
            blk = Element("block", type="comment")
            fld = SubElement(blk, "field", name="TEXT")
            fld.text = text[2:].strip()
            return blk
        # fallback raw
        blk = Element("block", type="quorum_statement")
        fld = SubElement(blk, "field", name="CODE")
        fld.text = text
        return blk

    # ---------- tokenize (indent, text) ----------
    toks = []
    for raw in code_input.splitlines():
        if not raw.strip():
            continue
        toks.append((_indent_count(raw), raw.strip()))
    i = 0

    # ---------- recursive descent over indentation ----------
    def parse_block_list(base_indent: int):
        """Parse a list of sibling statements at base_indent."""
        nonlocal i
        blocks = []
        while i < len(toks):
            indent, text = toks[i]
            if indent < base_indent:
                break
            if indent > base_indent:
                # leave for caller (we only consume base level here)
                break

            if text.startswith("if"):
                blocks.append(parse_if(indent))
                continue
            if text.startswith("repeat"):
                blocks.append(parse_repeat(indent))
                continue
            if text.startswith("while"):
                blocks.append(parse_while(indent))
                continue
            if text.startswith("elseif") or text.startswith("else"):
                # belongs to a preceding 'if' — let caller handle
                break

            blocks.append(_simple_block(text))
            i += 1
        return blocks

    def parse_if(if_indent: int):
        """Parse: if (...) then [body]; {elseif (...) then [body]}*; [else [body]]"""
        nonlocal i
        # consume 'if ... then'
        _, if_text = toks[i]; i += 1

        blk = Element("block", type="controls_if")
        elseif_count = 0
        has_else = False

        # IF0 + DO0
        v0 = SubElement(blk, "value", name="IF0")
        v0.append(_bool_block_from_text(if_text))
        do0 = SubElement(blk, "statement", name="DO0")

        # body of IF0 (one indent deeper)
        if i < len(toks) and toks[i][0] > if_indent:
            body_indent = toks[i][0]
            body_blocks = parse_block_list(body_indent)
            head = _chain(body_blocks)
            if head is not None:
                do0.append(head)

        # zero or more elseif (same indent as 'if')
        while i < len(toks) and toks[i][0] == if_indent and toks[i][1].startswith("elseif"):
            _, elseif_text = toks[i]; i += 1
            idx = elseif_count + 1
            v = SubElement(blk, "value", name=f"IF{idx}")
            v.append(_bool_block_from_text(elseif_text))
            do = SubElement(blk, "statement", name=f"DO{idx}")
            if i < len(toks) and toks[i][0] > if_indent:
                body_indent = toks[i][0]
                body_blocks = parse_block_list(body_indent)
                head = _chain(body_blocks)
                if head is not None:
                    do.append(head)
            elseif_count += 1

        # optional else (same indent as 'if')
        if i < len(toks) and toks[i][0] == if_indent and toks[i][1].startswith("else"):
            i += 1
            has_else = True
            do = SubElement(blk, "statement", name="ELSE")
            if i < len(toks) and toks[i][0] > if_indent:
                body_indent = toks[i][0]
                body_blocks = parse_block_list(body_indent)
                head = _chain(body_blocks)
                if head is not None:
                    do.append(head)

        # set mutation
        mut = SubElement(blk, "mutation")
        mut.set("elseif", str(elseif_count))
        mut.set("else", "1" if has_else else "0")

        return blk

    def parse_repeat(rep_indent: int):
        nonlocal i
        _, line = toks[i]; i += 1
        blk = Element("block", type="controls_repeat_ext")
        val = SubElement(blk, "value", name="TIMES")
        num = SubElement(val, "block", type="math_number")
        nf = SubElement(num, "field", name="NUM")
        parts = line.split()
        nf.text = parts[1] if len(parts) >= 2 and parts[1].isdigit() else "5"
        do = SubElement(blk, "statement", name="DO")
        if i < len(toks) and toks[i][0] > rep_indent:
            body_indent = toks[i][0]
            body_blocks = parse_block_list(body_indent)
            head = _chain(body_blocks)
            if head is not None:
                do.append(head)
        return blk

    def parse_while(wh_indent: int):
        nonlocal i
        _, line = toks[i]; i += 1
        blk = Element("block", type="controls_whileUntil")
        mode = SubElement(blk, "field", name="MODE"); mode.text = "WHILE"
        val = SubElement(blk, "value", name="BOOL")
        val.append(_bool_block_from_text(line))
        do = SubElement(blk, "statement", name="DO")
        if i < len(toks) and toks[i][0] > wh_indent:
            body_indent = toks[i][0]
            body_blocks = parse_block_list(body_indent)
            head = _chain(body_blocks)
            if head is not None:
                do.append(head)
        return blk

    # ---------- top-level ----------
    i = 0
    top_blocks = parse_block_list(0)
    root = Element("xml", xmlns="https://developers.google.com/blockly/xml")
    head = _chain(top_blocks)
    if head is not None:
        root.append(head)
    return tostring(root, encoding="unicode")

def louis_translate(text_input, table, file_name):
    if getattr(sys, 'frozen', False):  # Running as an executable
        base_dir = os.path.dirname(sys.executable)
        table_folder = os.path.join(base_dir, '_internal', 'tables')
    else:  # Running as a script
        base_dir = os.path.dirname(os.path.abspath(__file__))
        table_folder = os.path.join(base_dir, "liblouis/tables")

    dots_path = os.path.join(table_folder, "braille-patterns.cti")
    #nemeth_path = os.path.join(table_folder, "nemethdefs.cti")
    table_path = os.path.join(table_folder, table)
    
    translation = louis.translateString([dots_path, table_path], text_input)
    # translation = louis.translateString([nemeth_path, table_path], text_input)
    
    return translation
