import sys
import json
import util
import cfg
import mylive

def get_liveness(block_map, succs, preds):
    uses_map = mylive.get_var_map(block_map, mylive.uses)
    kill_map = mylive.get_var_map(block_map, mylive.kill)
    return mylive.liveness_analysis(uses_map, kill_map, succs, preds)

def dce_block(block, live_in, live_out):
    todel = set()
    for i, instr in reversed(list(enumerate(block))):
        dest, args, op, val = util.grab(instr)
        if dest:
            if not dest in live_out:
                todel.add(i)
            else:
                live_out.discard(dest)
                if args: live_out |= set(args)
        elif args: live_out |= set(args)
    changed = len(todel) > 0
    if changed: block[:] = [instr for i, instr in enumerate(block) if not i in todel]
    return changed

def dce_blocks(block_map, live_in, live_out):
    changed = False
    for name, block in block_map.items():
        changed |= dce_block(block, live_in[name], live_out[name])
    return changed

def dce(block_map, succs, preds):
    live_in, live_out = get_liveness(block_map, succs, preds)
    while dce_blocks(block_map, live_in, live_out):
        live_in, live_out = get_liveness(block_map, succs, preds)

if __name__ == "__main__":
    prog = json.load(sys.stdin)
    for func in prog["functions"]:
        block_map, succs, preds, entry = cfg.init_cfg(func["instrs"])
        dce(block_map, succs, preds)
        instrs = list(cfg.reassemble(block_map, entry))
        cfg.optimize_terminators(instrs)
        func["instrs"] = instrs
    json.dump(prog, sys.stdout, indent=4)
