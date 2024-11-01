import sys
import json
import util
import cfg
import dflow

"""
Note: FOLODABLE_OPS was copied from lvn.py and modified
"""

FOLDABLE_OPS = {
        "id": lambda args: args[0],
        "add": lambda args: args[0] + args[1],
        "mul": lambda args: args[0] * args[1],
        "sub": lambda args: args[0] - args[1],
        "div": lambda args: args[0] // args[1],
        "gt": lambda args: args[0] > args[1],
        "lt": lambda args: args[0] < args[1],
        "ge": lambda args: args[0] >= args[1],
        "le": lambda args: args[0] <= args[1],
        "ne": lambda args: args[0] != args[1],
        "eq": lambda args: args[0] == args[1],
        "or": lambda args: args[0] or args[1],
        "and": lambda args: args[0] and args[1],
        "not": lambda args: not args[0]
    }

def const_merge(name, succs, preds, const_in, const_out):
    common_vars = util.intersect([const_out[p].keys() for p in preds[name]])
    in_ = {}
    for v in common_vars:
        s = set()
        for p in preds[name]:
            s.add(const_out[p][v])
        if len(s) == 1:
            in_[v] = s.pop()
    return in_

def const_transfer(block, in_):
    out_ = {}
    for instr in block:
        d, args, op, v = util.grab(instr)
        if op == "const": out_[d] = (v, instr.get("type"))
        elif args and set(args).issubset([var for var, val in in_.items() if val]) and op in FOLDABLE_OPS:
            out_[d] = (FOLDABLE_OPS[op]([in_[arg][0] for arg in args]), instr.get("type"))
    return out_

def const_analysis(block_map, succs, preds):
    #  return dflow.dflow_forward(block_map, succs, preds, dict(), const_merge, const_transfer)
    const_in = {name: dict() for name in block_map}
    const_out = {name: dict() for name in block_map}
    worklist = set(block_map.keys())
    while worklist:
        name = worklist.pop()
        in_ = const_merge(name, succs, preds, const_in, const_out)
        out_ = const_transfer(block_map[name], in_)
        #  out_ = transfer(name, block_map, in_, **kwargs)
        if in_ != const_in[name] or out_ != const_out[name]:
            const_in[name] = in_
            const_out[name] = out_
            worklist.update(succs[name])
    return const_in, const_out

def get_const_in(block_map, succs, preds):
    const_in, const_out = const_analysis(block_map, succs, preds)
    return const_in

def cpf_block(block, const):
    changed = False
    for instr in block:
        dest, args, op, val = util.grab(instr)
        if not dest: continue
        if op == "const":
            const[dest] = (val, instr.get("type"))
        elif set(args).issubset(set(const.keys())) and op in FOLDABLE_OPS:
            changed = True
            instr["op"] = "const"
            instr["value"] = FOLDABLE_OPS[op]([const[arg][0] for arg in args])
            del instr["args"]
            const[dest] = (instr["value"], instr.get("type"))
        elif dest in const and op != "const":
            del const[dest]
    return changed

def cpf_blocks(block_map, const_in):
    changed = False
    for name, block in block_map.items():
        changed |= cpf_block(block, const_in[name])
    return changed

def cpf(block_map, succs, preds):
    const_in, const_out = const_analysis(block_map, succs, preds)
    while cpf_blocks(block_map, const_in):
        const_in, const_out = const_analysis(block_map, succs, preds)

def cprop(block_map, succs, preds):
    const_in, const_out = const_analysis(block_map, succs, preds)
    for name, block in block_map.items():
        for v in const_in[name]:
            block.insert(0, {"op": "const", "value": const_in[name][v][0], "type": const_in[name][v][1], "dest": v})

if __name__ == "__main__":
    prog = json.load(sys.stdin)
    for func in prog["functions"]:
        block_map, succs, preds, entry = cfg.init_cfg(func["instrs"])
        cpf(block_map, succs, preds)
        cprop(block_map, succs, preds)
        instrs = list(cfg.reassemble(block_map, entry))
        cfg.optimize_terminators(instrs)
        func["instrs"] = instrs
    json.dump(prog, sys.stdout, indent=4)
