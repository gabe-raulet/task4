import sys
import json

def grab(instr):
    return instr.get("dest"), instr.get("args"), instr.get("op"), instr.get("value")

def straight_dce(instrs):
    live = set()
    todel = set()
    for i, instr in reversed(list(enumerate(instrs))):
        dest, args, op, val = grab(instr)
        if dest:
            if not dest in live:
                todel.add(i)
            else:
                live.discard(dest)
                if args: live |= set(args)
        elif args: live |= set(args)
    instrs[:] = [instr for i, instr in enumerate(instrs) if not i in todel]

if __name__ == "__main__":
    prog = json.load(sys.stdin)
    for func in prog["functions"]:
        straight_dce(func["instrs"])
    json.dump(prog, sys.stdout, indent=4)
