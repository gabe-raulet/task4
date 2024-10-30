import sys
import json
import util
import cfg
from collections import defaultdict

prog = util.read_bril("t1.bril")
instrs = prog["functions"][0]["instrs"]

def_map = defaultdict(list)
use_map = defaultdict(list)
defs = []
uses = []
gen_map = []
kill_map = []

for i, instr in enumerate(instrs):
    dest = instr.get("dest")
    args = instr.get("args")
    if dest:
        defs.append((dest, i))
        def_map[dest].append(i)
    if args:
        for j, arg in enumerate(args):
            uses.append((arg, i, j))
            use_map[arg].append((i, j))

def_map = dict(def_map)
use_map = dict(use_map)
kill_map = dict()

for i, instr in enumerate(instrs):
    dest = instr.get("dest")
    if dest: kill_map[i] = set(def_map[dest]) - {i}
    else: kill_map[i] = set()

reach_in = [set() for _ in range(len(instrs))]
reach_out = [set() for _ in range(len(instrs))]

for i, instr in enumerate(instrs):
    if i > 0: reach_in[i] = reach_out[i-1].copy()
    dest = instr.get("dest")
    if not dest:
        reach_out[i] = reach_in[i].copy()
    else:
        reach_out[i] = {i}.union(reach_in[i] - kill_map[i])

def use_def(var, pos):
    """
    find the definition ofs `var` that reach the use of `var` at `pos`
    """
    for d in reach_in[pos]:
        if d in def_map[var]:
            yield d

