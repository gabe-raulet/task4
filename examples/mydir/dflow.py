import sys
import json
import util
import cfg

"""
Start by implementing a forward flow generic data-flow analysis
"""

def dflow_forward(block_map, succs, preds, initial, merge, transfer):
    dflow_in = {name: initial for name in block_map}
    dflow_out = {name: initial for name in block_map}
    worklist = set(block_map.keys())
    while worklist:
        name = worklist.pop()
        in_ = merge(name, succs, preds, dflow_in, dflow_out)
        out_ = transfer(block_map[name], in_)
        if in_ != dflow_in[name] or out_ != dflow_out[name]:
            dflow_in[name] = in_
            dflow_out[name] = out_
            worklist.update(succs[name])
    return dflow_in, dflow_out
