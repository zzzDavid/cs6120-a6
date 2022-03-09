import copy

def cfg_from_ssa(cfg):
    for _, block in cfg.items():
        for instr in block.instrs:
            if instr.get("op") == "phi":
                dest = instr["dest"]
                typ = instr["type"]
                for i, label in enumerate(instr["labels"]):
                    var = instr["args"][i]
                    if var == 'undef': continue
                    copy_instr = {"op": "id", "type": typ, "args": [var], "dest": dest}
                    cfg[label].instrs.insert(-1, copy_instr)
        block.instrs = [
            instr
            for instr in copy.deepcopy(block.instrs)
            if instr.get("op") != "phi"
        ]
