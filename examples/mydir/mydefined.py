import sys
import json
import util
import cfg

def def_analysis(block_map, succs, preds):
    def_in, def_out = {}, {}
    for name, block in block_map.items():
        def_in[name] = set()
        def_out[name] = set()
    worklist = set(block_map.keys())
    while worklist:
        name = worklist.pop()
        in_ = util.unionize([def_out[p] for p in preds[name]])
        out_ = in_.union([inst.dest for inst in util.parse_instructions(block_map[name]) if inst.dest])
        if in_ != def_in[name] or out_ != def_out[name]:
            def_in[name] = in_
            def_out[name] = out_
            worklist.update(succs[name])
    return def_in, def_out

if __name__ == "__main__":
    prog = json.load(sys.stdin)
    for func in prog["functions"]:
        block_map, succs, preds, entry = cfg.init_cfg(func["instrs"])
        def_in, def_out = def_analysis(block_map, succs, preds)
        for name in block_map:
            in_ = " ".join(sorted([v for v in def_in[name]]))
            out_ = " ".join(sorted([v for v in def_out[name]]))
            print(f"{name}:")
            print(f"  in: {in_}")
            print(f"  out: {out_}")
