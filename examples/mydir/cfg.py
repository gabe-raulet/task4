import sys
import json
import util

def form_blocks(instrs):
    block = []
    for instr in instrs:
        if "op" in instr:
            block.append(instr)
            if instr["op"] in {"jmp", "br", "ret"}:
                yield block
                block = []
        else:
            if block: yield block
            block = [instr]
    if block: yield block

def get_block_label(block):
    return block[0].get("label")

def add_labels(blocks):
    """
    Given a list of blocks, add labels to those blocks
    that don't already have them
    """
    for i, block in enumerate(blocks):
        if not "label" in block[0]:
            blocks[i].insert(0, {"label": f"bb{i+1}"})

def add_jmps(blocks):
    """
    Given a list of basic blocks, add explicit jump instructions
    """
    for i, block in enumerate(blocks[:-1]):
        if block[-1].get("op") not in {"jmp", "br", "ret"}:
            blocks[i] = block + [{"op": "jmp", "labels": [get_block_label(blocks[i+1])]}]

def add_rets(blocks):
    """
    Given a list of basic blocks, add explicit return instructions
    """
    block = blocks[-1]
    if block[-1].get("op") not in {"jmp", "br", "ret"}:
        blocks[-1] = block + [{"op": "ret", "args": []}]

def add_entry(blocks):
    """
    Add unique entry block if necessary
    """
    start = get_block_label(blocks[0])
    if start in util.unionize([instr.get("labels", []) for instr in util.flatten(blocks)]):
        entry = [{"label": f"pre.{start}"}, {"op": "jmp", "labels": [start]}]
        blocks.insert(0, entry)

def prepare_blocks_for_cfg(blocks):
    add_labels(blocks)
    add_jmps(blocks)
    add_rets(blocks)
    add_entry(blocks)

def init_block_map(blocks):
    block_map = dict()
    for block in blocks:
        block_map[get_block_label(block)] = block[1:]
    return block_map, get_block_label(blocks[0])

def init_cfg(instrs):
    blocks = list(form_blocks(instrs))
    prepare_blocks_for_cfg(blocks)
    block_map, entry = init_block_map(blocks)
    succs = {name : set() for name in block_map}
    preds = {name : set() for name in block_map}
    for name, block in block_map.items():
        for dest in block[-1].get("labels", []):
            succs[name].add(dest)
            preds[dest].add(name)
    return block_map, succs, preds, entry

def reassemble(block_map, entry):
    yield {"label": entry}
    for instr in block_map[entry]:
        yield instr
    for name, block in block_map.items():
        if name == entry: continue
        yield {"label": name}
        for instr in block:
            yield instr

def optimize_terminators(instrs):
    toremove = set()
    for i, instr in enumerate(instrs[:-1]):
        if instr.get("op") == "jmp" and instr["labels"][0] == instrs[i+1].get("label"):
            toremove.add(i)
    if instrs[-1].get("op") == "ret" and len(instrs[-1].get("args", [])) == 0:
        toremove.add(len(instrs)-1)
    util.remove_instrs(instrs, toremove)
    #  instrs[:] = [instr for i, instr in enumerate(instrs) if not i in toremove]

def main(prog, opt):
    for func in prog["functions"]:
        block_map, succs, preds, entry = init_cfg(func["instrs"])
        func["instrs"] = list(reassemble(block_map, entry))
        if opt: optimize_terminators(func["instrs"])

if __name__ == "__main__":
    prog = json.load(sys.stdin)
    main(prog, "-t" in sys.argv)
    json.dump(prog, sys.stdout, indent=4)
