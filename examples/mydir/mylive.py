import sys
import json
import util
import cfg

def uses(block):
    """
    Compute the set of variables used in `block` before they are assigned to
    """
    gen, defined = set(), set()
    for instr in util.parse_instructions(block):
        for v in instr.uses:
            if not v in defined:
                gen.add(v)
        if instr.dest:
            defined.add(instr.dest)
    return gen

def kill(block):
    """
    Compute set of variables in `block` that are assigned to
    """
    return set([instr.dest for instr in util.parse_instructions(block) if instr.dest])


def liveness(func_cfg):
    block_map, succs, preds, entry = func_cfg
    live_in, live_out, uses_map, kill_map = {}, {}, {}, {}
    for name, block in block_map.items():
        uses_map[name] = uses(block)
        kill_map[name] = kill(block)
        live_in[name] = set()
        live_out[name] = set()
    worklist = set(block_map.keys())
    while worklist:
        name = worklist.pop()
        out_ = util.unionize([live_in[s] for s in succs[name]])
        in_ = uses_map[name].copy().union(out_ - kill_map[name])
        if in_ != live_in[name] or out_ != live_out[name]:
            live_in[name] = in_
            live_out[name] = out_
            worklist.update(preds[name])
    return live_in, live_out

if __name__ == "__main__":
    prog = json.load(sys.stdin)
    for func in prog["functions"]:
        func_cfg = cfg.init_cfg(func["instrs"])
        live_in, live_out = liveness(func_cfg)
        for name in func_cfg[0]:
            in_ = " ".join(sorted([v for v in live_in[name]]))
            out_ = " ".join(sorted([v for v in live_out[name]]))
            print(f"{name}:")
            print(f"  in: {in_}")
            print(f"  out: {out_}")
