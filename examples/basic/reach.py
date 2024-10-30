import sys
import json
import util
import cfg
import dflow
from collections import defaultdict

def bfs(block_map, succs, entry):
    queue = [entry]
    visited = set([entry])
    while queue:
        u = queue.pop(0)
        yield u
        for v in succs[u]:
            if not v in visited:
                queue.append(v)
                visited.add(v)

def get_use_def_info(block_map, succs, entry):

    i = 0
    line_map = {}
    for name in bfs(block_map, succs, entry):
        line_map[name] = i
        i += len(block_map[name])

    def2lines = defaultdict(list)
    use2lines = defaultdict(list)
    line2block = dict()

    for name, block in block_map.items():
        line = line_map[name]
        for i, instr in enumerate(block):
            line2block[line + i] = (name, i)
            dest = instr.get("dest")
            args = instr.get("args")
            if dest:
                def2lines[dest].append(line + i)
            if args:
                for arg in set(args):
                    use2lines[arg].append(line + i)

    def2lines = dict(def2lines)
    use2lines = dict(use2lines)

    return line_map, def2lines, use2lines, line2block

def reach_transfer(name, block_map, reach_in_, **kwargs):
    line_map = kwargs["line_map"]
    def2lines = kwargs["def2lines"]
    use2lines = kwargs["use2lines"]
    line = line_map[name]
    block = block_map[name]
    reach = reach_in_.copy()
    for i, instr in enumerate(block):
        dest = instr.get("dest")
        if dest:
            kill = set(def2lines[dest]) - {i+line}
            reach = {i+line}.union(reach - kill)
    return reach

def reach_merge(out_, preds):
    return util.unionize([out_[pred] for pred in preds])

def reach_analysis(block_map, succs, preds, entry):
    line_map, def2lines, use2lines, line2block = get_use_def_info(block_map, succs, entry)
    reach_in, reach_out = dflow.dflow_forward(reach_merge, reach_transfer, block_map, succs, preds, set(), def2lines=def2lines, use2lines=use2lines, line_map=line_map)
    return reach_in, reach_out, line2block, def2lines, use2lines, line_map

def init_use_def_chain(block_map, reach_in, def2lines, use2lines, line_map):

    ud = {}
    for v, uses in use2lines.items():
        for use in uses:
            ud[(v, use)] = set()

    for name, block in block_map.items():
        reach_ = reach_in[name].copy()
        line = line_map[name]
        for i, instr in enumerate(block):
            args = instr.get("args")
            dest = instr.get("dest")
            if args:
                for v in set(args):
                    if not v in def2lines:
                        continue
                    for d in reach_:
                        for d2 in def2lines[v]:
                            if d == d2:
                                ud[(v, i+line)].add(d)
            if dest:
                kill = set(def2lines[dest]) - {i+line}
                reach_ = {i+line}.union(reach_ - kill)
    return ud

def init_def_use_chain(ud):
    du = defaultdict(set)
    for u in ud:
        for d in ud[u]:
            du[d].add(u)
    return dict(du)

#  prog = util.read_bril("t1.bril")
#  instrs = prog["functions"][0]["instrs"]
#  block_map, succs, preds, entry = cfg.init_cfg(instrs)
#  reach_in, reach_out, line2block, def2lines, use2lines, line_map = reach_analysis(block_map, succs, preds, entry)
#  ud = init_use_def_chain(block_map, reach_in, def2lines, use2lines, line_map)
#  du = init_def_use_chain(ud)

