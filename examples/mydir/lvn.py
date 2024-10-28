import sys
import json
import util
import cfg
import briltxt

class lvntable(object):

    def __init__(self):
        self.num2var = {} # map value number to canonical variable
        self.var2num = {} # map variable to value number
        self.val2num = {} # map value expression to value number
        self.fresh = 0

    def add_new_value_number(self, var):
        if var in self.var2num:
            return self.var2num[var]
        self.var2num[var] = self.fresh
        self.fresh += 1
        self.num2var[self.var2num[var]] = var
        return self.var2num[var]

    def get_argnums(self, args):
        return [self.var2num[var] for var in args]

    def get_argvars(self, argnums):
        return [self.num2var[num] for num in argnums]

    def add_id_var(self, dest, var):
        self.var2num[dest] = self.var2num[var]

    def add_expr(self, instr):
        dest, args, op, cval = util.grab(instr)
        argnums = self.get_argnums(args)
        if op in {"and", "or", "add", "mul"}:
            argnums = sorted(argnums)
        val = tuple([op] + self.get_argnums(args))
        if not val in self.val2num:
            self.val2num[val] = self.add_new_value_number(dest)
        else:
            instr["op"] = "id"
            instr["args"] = [self.num2var[self.val2num[val]]]
            self.var2num[dest] = self.val2num[val]

    def __repr__(self):
        return f"var2num={self.var2num}\nnum2var={self.num2var}\nval2num={self.val2num}"

def lvn_block(instrs):

    table = lvntable()

    for instr in instrs:
        dest, args, op, cval = util.grab(instr)
        if args:
            for var in args:
                table.add_new_value_number(var)
            argnums = table.get_argnums(args)
            instr["args"] = table.get_argvars(argnums)
            #  if dest: table.clobber_update(dest)
            if op == "id":
                table.add_id_var(dest, args[0])
            elif not op in {"call", "ret", "print"}:
                table.add_expr(instr)
        #  print(table)
        #  print(briltxt.instr_to_string(instr) + "\n")

def lvn(block_map, succs, preds):
    for name, block in block_map.items():
        lvn_block(block)

if __name__ == "__main__":
    prog = json.load(sys.stdin)
    for func in prog["functions"]:
        block_map, succs, preds, entry = cfg.init_cfg(func["instrs"])
        lvn(block_map, succs, preds)
        instrs = list(cfg.reassemble(block_map, entry))
        cfg.optimize_terminators(instrs)
        func["instrs"] = instrs
    json.dump(prog, sys.stdout, indent=4)
