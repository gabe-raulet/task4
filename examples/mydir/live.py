import sys
import json
from collections import namedtuple
import cfg

def uses(block):
    """
    Compute the set of variables used in `block` before they are assigned to
    """
    gen, defined = set(), set()
    for instr in cfg.parse_instructions(block):
        for v in instr.uses:
            if not v in defined:
                gen.add(v)
        if instr.kill:
            defined.add(instr.kill)
    return gen

def kill(block):
    """
    Compute set of variables in `block` that are assigned to
    """
    return set([instr.kill for instr in cfg.parse_instructions(block) if instr.kill])


def liveness(block_map, succs, preds, entry):
    live_in, live_out, uses_map, kill_map = {}, {}, {}, {}
    for name, block in block_map.items():
        uses_map[name] = uses(block)
        kill_map[name] = kill(block)
        live_in[name] = set()
        live_out[name] = set()
    worklist = set(block_map.keys())
    while worklist:
        name = worklist.pop()
        out_ = cfg.unionize([live_in[s] for s in succs[name]])
        in_ = uses_map[name].copy().union(out_ - kill_map[name])
        if in_ != live_in[name] or out_ != live_out[name]:
            live_in[name] = in_
            live_out[name] = out_
            worklist.update(preds[name])
    return live_in, live_out

if __name__ == "__main__":
    prog = json.load(sys.stdin)
    for func in prog["functions"]:
        block_map, succs, preds, entry = cfg.init_cfg(func["instrs"])
        live_in, live_out = liveness(block_map, succs, preds, entry)
        for name in block_map:
            print(f"{name}:")
            ins = " ".join(live_in[name])
            outs = " ".join(live_out[name])
            print(f"  in: {ins}")
            print(f"  out: {outs}")
