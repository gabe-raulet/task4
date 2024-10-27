import sys
import json
from collections import namedtuple
import briltxt

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
    if not items:
        return set()

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

def read_bril(bril_fname):
    """
    Read a bril file and convert to json within python for debugging purposes
    """
    return json.loads(briltxt.parse_bril(open(bril_fname, "r").read()))
