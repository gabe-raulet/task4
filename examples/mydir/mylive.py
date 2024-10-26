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

def get_var_map(block_map, block_func):
    var_map = {}
    for name, block in block_map.items():
        var_map[name] = block_func(block)
    return var_map

def liveness_analysis(uses_map, kill_map, succs, preds):
    live_in, live_out = {}, {}
    for name in uses_map:
        live_in[name] = set()
        live_out[name] = set()
    worklist = set(uses_map.keys())
    while worklist:
        name = worklist.pop()
        out_ = util.unionize([live_in[s] for s in succs[name]])
        in_ = uses_map[name].copy().union(out_ - kill_map[name])
        if in_ != live_in[name] or out_ != live_out[name]:
            live_in[name] = in_
            live_out[name] = out_
            worklist |= preds[name]
    return live_in, live_out
