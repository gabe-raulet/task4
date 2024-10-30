import sys
import json
import util

def dflow_forward(merge, transfer, block_map, succs, preds, init, **kwargs):
    dflow_in = {name: set() for name in block_map}
    dflow_out = {name: set() for name in block_map}
    worklist = set(block_map.keys())
    while worklist:
        name = worklist.pop()
        in_ = merge(dflow_out, preds[name])
        out_ = transfer(name, block_map, in_, **kwargs)
        if in_ != dflow_in[name] or out_ != dflow_out[name]:
            dflow_in[name] = in_
            dflow_out[name] = out_
            worklist.update(succs[name])
    return dflow_in, dflow_out
