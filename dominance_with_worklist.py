import copy



def worklist_algo(cfg, merge_func, transfer_func, printer=None):
    """The worklist algorithm
    - cfg: a dictionary of blocks
    """
    # ins and outs are dicts: {str : set()}
    # initialize
    ins = dict()
    outs = dict()
    for label, _ in cfg.items():
        ins[label] = set()
        outs[label] = set()
    worklist = copy.deepcopy(cfg)
    while len(worklist) > 0:
        # pick any block from worklist
        # I'll just pick the first one
        label = list(worklist.keys())[0]
        bb = worklist.pop(label)
        bb_ins = [outs[label] for label in bb.pred]
        bb_ins_merged = merge_func(bb_ins)
        ins[label] = bb_ins_merged
        bb_outs  = transfer_func(bb, bb_ins_merged)
        if len(bb_outs) != len(outs[label]):
            outs[label] = bb_outs
            for succ in bb.succ:
                worklist[succ] = cfg[succ]
    
    if printer is not None:
        printer(ins, outs)
    return outs



def merge(ins):
    """
    - ins: a list of sets
    - return: a set
    """
    res = set()
    if len(ins) > 0:
        res.update(ins[0])
    for i in ins:
        if len(i) == 0: continue
        res = res.intersection(i)
    return res

def transfer(bb, ins):
    """
    - bb: BasicBlock
    - ins: a set of dominator
    - return: a set dominators
    """
    label = bb.instrs[0]['label']
    ins.add(label)
    return ins

def find_dominator_worklist(cfg):
    return worklist_algo(cfg, merge, transfer)