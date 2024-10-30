import sys
import json
import util
import dflow
import cfg
from collections import defaultdict
from unionfind import UnionFind

def alias(func):

    instrs = func["instrs"]

    def merge(x, y, uf, pts):
        x = uf[uf.find(x)]
        y = uf[uf.find(y)]
        if x == y: return
        uf.union(x, y)
        merge(pts[x], pts[y], uf, pts)

    pts = dict()
    allocs = set()

    for arg in func.get("args", []):
        if "ptr" in arg["type"]:
            pts[arg["name"]] = arg["name"]

    alloc = 1
    for instr in instrs:
        t = instr.get("type")
        if t and "ptr" in t:
            dest = instr.get("dest")
            op = instr.get("op")
            if op == "alloc":
                pts[dest] = f"h{alloc}"
                allocs.add(pts[dest])
                pts[pts[dest]] = pts[dest]
                alloc += 1
            else:
                pts[dest] = dest

    def point(a, b, uf, pts):
        if not pts[a]: pts[a] = pts[b]
        else: merge(pts[a], pts[b], uf, pts)

    uf = UnionFind(pts.keys())

    for instr in instrs:
        op = instr.get("op")
        dest = instr.get("dest")
        args = instr.get("args")
        if dest in pts:
            if op == "id" or op == "ptradd":
                a, b = dest, args[0]
                point(a, b, uf, pts)
            elif op == "load" and args[0] in pts:
                a, b = dest, args[0]
                point(a, pts[b], uf, pts)
        elif op == "store" and args[1] in pts:
            a, b = args
            point(pts[a], b, uf, pts)

    pts = {p : uf.component(v) for p, v in pts.items() if not p in allocs}

    return pts

if __name__ == "__main__":
    prog = json.load(sys.stdin)
    for func in prog["functions"]:
        pts = alias(func)
        print(func["name"])
        for p, comp in pts.items(): print(f"p={p}\tcomp={comp}")
        print("\n")
    #  json.dump(prog, sys.stdout, indent=4)
