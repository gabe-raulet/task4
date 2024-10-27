import sys
import json

def get_var(arg, var):
    return f"{arg}.{var[arg]}"

def update_args(instr, var):
    args = instr.get("args", [])
    for i, arg in enumerate(args):
        if arg in var:
            args[i] = get_var(arg, var)

def update_dest(instr, var):
    dest = instr.get("dest")
    if dest:
        if dest in var: var[dest] += 1
        else: var[dest] = 0
        instr["dest"] = get_var(dest, var)

def straight_ssa(instrs):
    var = {}
    for instr in instrs:
        update_args(instr, var)
        update_dest(instr, var)

if __name__ == "__main__":
    prog = json.load(sys.stdin)
    for func in prog["functions"]:
        straight_ssa(func["instrs"])
    json.dump(prog, sys.stdout, indent=4)
