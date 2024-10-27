import sys
import json

def grab(instr):
    return instr.get("dest"), instr.get("args"), instr.get("op"), instr.get("value")

def straight_cprop(instrs):
    const_map = {}
    for instr in instrs:
        dest, args, op, val = grab(instr)
        if not dest: continue
        if op == "const":
            # put constant value into map
            const_map[dest] = val
        elif op == "id" and args[0] in const_map:
            # replace copy assignment with constant expression
            instr["op"] = "const"
            instr["value"] = const_map[args[0]]
            del instr["args"]
            const_map[dest] = instr["value"]
        elif op == "add" and args[0] in const_map and args[1] in const_map:
            # constant fold addition instruction
            instr["op"] = "const"
            instr["value"] = const_map[args[0]] + const_map[args[1]]
            del instr["args"]
            const_map[dest] = instr["value"]
        elif dest in const_map and op != "const":
            # clobbered variable (shouldn't happen in SSA!)
            del const_map[dest]

if __name__ == "__main__":
    prog = json.load(sys.stdin)
    for func in prog["functions"]:
        straight_cprop(func["instrs"])
    json.dump(prog, sys.stdout, indent=4)
