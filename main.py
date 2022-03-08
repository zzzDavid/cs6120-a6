import argparse
import json
import copy
import sys

from basic_block import form_basic_blocks
from control_flow_graph import *
from dominance_with_worklist import find_dominator_worklist, worklist_algo
from verifier import DominatorVerifier
from visualizer import CFGVisualizer, DomTreeVisualizer
from printer import dom_tree_printer, frontier_printer

def find_dominators(cfg):
    """
    - cfg: dict(str, BasicBlock)
    """
    dom = dict() # str -> set(str)
    while True:
        changed = False
        for vertex, bb in cfg.items():
            if vertex not in dom:
                dom[vertex] = list()
            # find all predecessors' dominators
            pred_doms = [dom[p] for p in bb.pred if p in dom]
            common_doms = set.intersection(*pred_doms) if len(pred_doms) > 0 else set()
            common_doms.add(vertex) # reflexive
            if not common_doms == dom[vertex]:
                dom[vertex] = common_doms
                changed = True
        if not changed: break
    return dom

class Node():
    def __init__(self, name) -> None:
        self.name = name
        self.preds = []
        self.succs = []

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
                if dd == d: continue
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

def main(args):
    # get options
    dom_print = args.dom
    domtree = args.domtree
    frontier = args.frontier
    worklist = args.worklist
    verify = args.verify
    viz = args.visualize
    file = args.filename

    if file is not None:
        with open(file, "r") as infile:
           prog = json.load(infile)
    else: 
        prog = json.load(sys.stdin)

    for func in prog['functions']:
        blocks = form_basic_blocks(func['instrs'])
        blocks = [b for b in blocks if len(b) > 0]
        cfg = CFG(blocks).cfg
        if viz:        
            cfg_visualizer = CFGVisualizer(cfg, func['name'] + '-cfg')
            cfg_visualizer.show()

        if worklist:
            dom = find_dominator_worklist(cfg)
        else:
            dom = find_dominators(cfg)

        if dom_print:
            # frontier printer also works for dom
            frontier_printer(dom)
        
        if verify:
            dom_verifier = DominatorVerifier(cfg, dom)
            if dom_verifier.verify():
                print("dom ok")
            else:
                print("dom not ok")

        if domtree:
            dom_tree = find_dom_tree(dom, cfg)
            if viz:
                dom_tree_vis = DomTreeVisualizer(dom_tree, func['name'] + '-domtree')
                dom_tree_vis.show()
            dom_tree_printer(dom_tree)
        
        if frontier:
            dom_frontier = find_dom_frontier(dom, cfg)
            frontier_printer(dom_frontier)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-dom', dest='dom',
                        default=False, action='store_true',
                        help='print dominator')
    parser.add_argument('-domtree', dest='domtree',
                        default=False, action='store_true',
                        help='print dominance tree')
    parser.add_argument('-frontier', dest='frontier',
                        default=False, action='store_true',
                        help='print dominance frontier')
    parser.add_argument('-worklist', dest='worklist',
                        default=False, action='store_true',
                        help='use worklist algorithm to find dominator')
    parser.add_argument('-verify', dest='verify',
                        default=False, action='store_true',
                        help='verify dominance result')
    parser.add_argument('-visualize', dest='visualize',
                        default=False, action='store_true',
                        help='visualize results')
    parser.add_argument('-f', dest='filename', 
                        action='store', type=str, help='json file')
    args = parser.parse_args()
    main(args)