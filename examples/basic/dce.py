import sys
import json
import util
import reach
import cfg

def dce(block_map, succs, preds, entry):
    while True:
        reach_in, reach_out, line2block, def2lines, use2lines, line_map = reach.reach_analysis(block_map, succs, preds, entry)
        ud = reach.init_use_def_chain(block_map, reach_in, def2lines, use2lines, line_map)
        du = reach.init_def_use_chain(ud)
        changed = False
        for name, block in block_map.items():
            todel = set()
            line = line_map[name]
            for i, instr in enumerate(block):
                if instr.get("dest") and not i+line in du:
                    todel.add(i)
            if len(todel) > 0:
                util.remove_instrs(block, todel)
                changed = True
        if not changed:
            break

def main(prog):
    for func in prog["functions"]:
        block_map, succs, preds, entry = cfg.init_cfg(func["instrs"])
        dce(block_map, succs, preds, entry)
        func["instrs"] = list(cfg.reassemble(block_map, entry))
        cfg.optimize_terminators(func["instrs"])

if __name__ == "__main__":
    prog = json.load(sys.stdin)
    main(prog)
    json.dump(prog, sys.stdout, indent=4)
