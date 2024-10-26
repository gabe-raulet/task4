import sys
import json
import util
import cfg
import mylive

def dce_iter(block_map, succs, preds):
    uses_map = mylive.get_var_map(block_map, mylive.uses)
    kill_map = mylive.get_var_map(block_map, mylive.kill)
    live_in, live_out = mylive.liveness_analysis(uses_map, kill_map, succs, preds)
    changed = False
    for name, block in block_map.items():
        live = live_out[name].copy()
        toremove = set()
        for instr in reversed(list(util.parse_instructions(block))):
            if instr.dest:
                if instr.dest not in live:
                    toremove.add(instr.pos)
            live |= instr.uses
        if toremove:
            changed = True
            util.remove_instrs(block, toremove)
    return changed

def dce(block_map, succs, preds):
    while dce_iter(block_map, succs, preds):
        pass

if __name__ == "__main__":
    prog = json.load(sys.stdin)
    for func in prog["functions"]:
        block_map, succs, preds, entry = cfg.init_cfg(func["instrs"])
        dce(block_map, succs, preds)
        instrs = list(cfg.reassemble(block_map, entry))
        cfg.optimize_terminators(instrs)
        func["instrs"] = instrs
    json.dump(prog, sys.stdout, indent=4)
