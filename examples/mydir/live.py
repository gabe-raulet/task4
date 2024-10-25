import sys
import json
from collections import namedtuple

#  prog = json.load(open("straight.json"))
#  instrs = prog["functions"][0]["instrs"]

#  insts = list(parse_instructions(instrs))

#  live_in, live_out = {}, {}

#  for inst in insts:
    #  live_in[inst.pos] = set()
    #  live_out[inst.pos] = set()

#  worklist = insts[:]
#  while worklist:
    #  inst = worklist.pop()
    #  if inst.pos == len(insts) - 1: out_ = set()
    #  else: out_ = live_in[inst.pos+1]
    #  in_ = inst.uses.union(out_ - inst.kill)
    #  if in_ != live_in[inst.pos] or out_ != live_out[inst.pos]:
        #  live_in[inst.pos] = in_
        #  live_out[inst.pos] = out_
        #  worklist.append(insts[inst.pos-1])

#  if __name__ == "__main__":
    #  prog = json.load(sys.stdin)
    #  for func in prog["functions"]:
        #  instrs = func["instrs"]
        #  result = liveness(instrs)
        #  print(result)
