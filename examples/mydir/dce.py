import sys
import json
import util
import cfg
import mylive

def ldce_pass(block, live):
    toremove = set()
    for instr in reversed(list(util.parse_instructions(block))):
        if instr.dest:
            if instr.dest not in live:
                toremove.add(instr.pos)
        live |= instr.uses
    return toremove

def ldce(block, live):
    while True:
        toremove = ldce_pass(block, live)
        if not toremove: break
        util.remove_instrs(block, toremove)

def dce(block_map, live_out):
    for name, block in block_map.items():
        live = live_out[name].copy()
        ldce(block_map[name], live)

def main(prog):
    for func in prog["functions"]:
        func_cfg = cfg.init_cfg(func["instrs"])
        live_in, live_out = mylive.liveness(func_cfg)
        block_map, _, _, entry = func_cfg
        dce(block_map, live_out)
        func["instrs"] = list(cfg.reassemble(block_map, entry))
        cfg.optimize_terminators(func["instrs"])

if __name__ == "__main__":
    prog = json.load(sys.stdin)
    main(prog)
    json.dump(prog, sys.stdout, indent=4)

