import copy


class Node:
    """
    Represents node in the dominance tree
    """

    def __init__(self, name) -> None:
        self.name = name
        self.preds = []
        self.succs = []


def find_dominators(cfg):
    """
    - cfg: dict(str, BasicBlock)
    """
    dom = dict()  # str -> set(str)
    while True:
        changed = False
        for vertex, bb in cfg.items():
            if vertex not in dom:
                dom[vertex] = list()
            # find all predecessors' dominators
            pred_doms = [dom[p] for p in bb.pred if p in dom]
            common_doms = set.intersection(*pred_doms) if len(pred_doms) > 0 else set()
            common_doms.add(vertex)  # reflexive
            if not common_doms == dom[vertex]:
                dom[vertex] = common_doms
                changed = True
        if not changed:
            break
    return dom


def find_dom_tree(dom, cfg):
    """
    A dominator tree is a tree where each node's children are
    those nodes it immediately dominates. Because the immediate
    dominator is unique, it is a tree. The start node is the
    root of the tree.

    - dom: dict(str, set(str))
    - cfg: dict(str, BasicBlock)
    - return: dict(str, Node)
    """
    dom_tree = dict()
    for vertex in cfg.keys():
        # find immediate dominators
        dominators = copy.deepcopy(dom[vertex])
        dominators.remove(vertex)
        idom = list()
        for d in dominators:
            # find all nodes that are dominated by d
            domed = list()
            for v, doms in dom.items():
                if d in doms:
                    domed.append(v)
            # if a vertex's dominator doesn't dominate
            # other vertex's dominator, then it's an
            # immediate dominator
            immediate = True
            for dd in dominators:
                if dd == d:
                    continue
                if dd in domed:
                    immediate = False
                    break
            if immediate:
                idom.append(d)
        for parent in idom:
            if vertex not in dom_tree:
                dom_tree[vertex] = Node(vertex)
            if parent not in dom_tree:
                dom_tree[parent] = Node(parent)
            dom_tree[parent].succs.append(vertex)
            dom_tree[vertex].preds.append(parent)
    return dom_tree


def find_dom_frontier(dom, cfg):
    """
    The dominance frontier of a node d is the set of all
    nodes ni such that d dominates an immediate predecessor
    of ni, but d does not strictly dominate ni. It is the
    set of nodes where d's dominance stops.
    """
    dom_frontier = dict()
    for vertex in cfg.keys():
        dom_frontier[vertex] = set()
        # find all nodes that are dominated by vertex
        domed = list()
        for v, dominators in dom.items():
            if vertex in dominators:
                domed.append(v)
        # strictly dominate
        # domed.remove(vertex)
        for d in domed:
            # if d's successor is not dominated by vertex
            # it's on the frontier
            for successor in cfg[d].succ:
                if successor not in domed or successor == vertex:
                    dom_frontier[vertex].add(successor)
    return dom_frontier
