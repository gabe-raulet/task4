import sys
import json
from collections import namedtuple

Instruction = namedtuple("Instruction", ["uses", "dest", "pos", "instr"])

def remove_instrs(instrs, toremove):
    """
    Remove all instructions from `instrs` whose position is in `toremove`
    """
    instrs[:] = [instr for i, instr in enumerate(instrs) if not i in toremove]

def parse_instructions(instrs):
    """
    Parse `instrs` into Instruction objects
    """
    for pos, instr in enumerate(instrs):
        uses = set(instr.get("args", []))
        dest = instr.get("dest", None)
        yield Instruction(uses=uses, dest=dest, pos=pos, instr=instr)

def intersect(items):
    """
    Compute the intersection of the list of iterables `items`
    """
    result = set(items[0])
    for item in items[1:]:
        result.intersection_update(item)
    return result

def unionize(items):
    """
    Compute the union of the list of iterables `items`
    """
    result = set()
    for item in items:
        result.update(item)
    return result

def flatten(items):
    """
    Flatten a list of iterables `items` into single list
    """
    result = []
    for item in items:
        result += list(item)
    return result
