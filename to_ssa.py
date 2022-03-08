from dominator import find_dominators, find_dom_frontier
import copy

def get_def(cfg):
    """
    Produces a map from variable name to the set of block
    names, where the block defines the variable.
    """
    defs = dict()
    for block_name, basic_block in cfg.items():
        for instr in basic_block.instrs:
            if 'dest' in instr:
                var_name = instr['dest']
                if var_name not in defs:
                    defs[var_name] = set()
                defs[var_name].add(block_name)
    return defs

def find_phi(cfg, frontier):
    """
    Produces a map from block names that needs to insert
    Phi-nodes to a set of variable names
    """
    phi_blocks = dict()
    defs = get_def(cfg)
    for var_name, def_blocks in defs.items():
        def_blocks_copy = copy.deepcopy(def_blocks)
        for d in def_blocks_copy: # blocks where v is assigned
            for block in frontier[d]:
                # Add a phi-node unless we've done so
                if block not in phi_blocks:
                    phi_blocks[block] = set()
                phi_blocks[block].add(var_name)
                # Add block to Defs[v] because it now
                # writes to v
                defs[var_name].add(block)
    return phi_blocks

def cfg_to_ssa(cfg):
    dom = find_dominators(cfg)
    frontier = find_dom_frontier(dom, cfg)
    phi_blocks = find_phi(cfg, frontier)