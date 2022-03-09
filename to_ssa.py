from dominator import find_dominators, find_dom_frontier, find_dom_tree
import copy


def get_def(cfg):
    """
    Produces a map from variable name to the set of block
    names, where the block defines the variable.
    """
    defs = dict()
    types = dict()
    for block_name, basic_block in cfg.items():
        for instr in basic_block.instrs:
            if "dest" in instr:
                var_name = instr["dest"]
                if var_name not in defs:
                    defs[var_name] = set()
                defs[var_name].add(block_name)
                types[var_name] = instr["type"]
    return defs, types


def find_phi(cfg, frontier, defs):
    """
    Produces a map from block names that needs to insert
    Phi-nodes to a set of variable names
    """
    phi_blocks = dict()
    for var_name, def_blocks in defs.items():
        def_blocks_copy = copy.deepcopy(def_blocks)
        for d in def_blocks_copy:  # blocks where v is assigned
            for block in frontier[d]:
                # Add a phi-node unless we've done so
                if block not in phi_blocks:
                    phi_blocks[block] = set()
                phi_blocks[block].add(var_name)
                # Add block to Defs[v] because it now
                # writes to v
                defs[var_name].add(block)
    return phi_blocks


def rename_var(cfg, defs, phi_blocks, dom_tree):
    stack = dict()  # {old_name : list of new names}
    # initialize the stack
    for var_name in defs.keys():
        stack[var_name] = list()

    phi_node_info = {"dest": "", "labels": list(), "args": list()}
    block_to_phi = dict()  # stores block -> phi_node_info mapping
    # init block_to_phi
    for block_name in cfg.keys():
        # because each block may have a bunch of phi nodes
        # we use another dict: old_var_name -> phi_node_info
        if block_name not in phi_blocks:
            continue
        block_to_phi[block_name] = dict()
        for v in phi_blocks[block_name]:
            block_to_phi[block_name][v] = copy.deepcopy(phi_node_info)

    def _rename_block(stack, block_name, block):
        # save stack
        stack_stashed = copy.deepcopy(stack) 

        # rename phi nodes's destinations
        if block_name in phi_blocks:
            # if this block has phi node
            for v in phi_blocks[block_name]:
                new_dest = v + "." + str(len(stack[v]))
                stack[v].append(new_dest)
                block_to_phi[block_name][v]["dest"] = new_dest

        for instr in block.instrs:
            # replace each argument with stack[old_name]
            if "args" in instr:
                new_args = [stack[arg][-1] if arg in stack else arg for arg in instr["args"]]
                instr["args"] = new_args
            if "dest" in instr:
                old_name = instr["dest"]
                new_dest = old_name + "." + str(len(stack[old_name]))
                instr["dest"] = new_dest
                # push the new name onto stack
                stack[old_name].append(new_dest)

        # update phi node arglist in successors
        for s in block.succ:
            if s not in phi_blocks:
                continue
            for p in phi_blocks[s]:
                # assuming p is for a variable v
                # make it read from stack[v]
                # we need to update the argument list
                # of the phi node in successors
                if block_name in defs[p]:
                    new_arg = stack[p][-1]
                else:
                    new_arg = 'undef'
                block_to_phi[s][p]["args"].append(new_arg)
                block_to_phi[s][p]["labels"].append(block_name)

        # Recusively rename all immediate dominance children
        for b in dom_tree[block_name].succs:
            _rename_block(stack, b, cfg[b])

        # pop all names we just pushed onto the stacks
        stack = copy.deepcopy(stack_stashed)

    entry_block_name = list(cfg.keys())[0]
    _rename_block(stack, entry_block_name, cfg[entry_block_name])

    return block_to_phi


def insert_phi_nodes(cfg, block_to_phi, types):
    """
    Actually insert phi nodes in the CFG
    """
    for block_name, phi_nodes in block_to_phi.items():
        for v, phi_node in phi_nodes.items():
            typ = types[v]
            phi_node = {
                "op": "phi",
                "dest": phi_node["dest"],
                "type": typ,
                "labels": phi_node["labels"],
                "args": phi_node["args"],
            }
            cfg[block_name].instrs.insert(0, phi_node)


def cfg_to_ssa(cfg):
    defs, types = get_def(cfg)
    dom = find_dominators(cfg)
    frontier = find_dom_frontier(dom, cfg)
    phi_blocks = find_phi(cfg, frontier, defs)
    dom_tree = find_dom_tree(dom, cfg)
    block_to_phi = rename_var(cfg, defs, phi_blocks, dom_tree)
    insert_phi_nodes(cfg, block_to_phi, types)