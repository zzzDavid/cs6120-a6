import argparse
import json
import copy
import sys

from basic_block import form_basic_blocks
from control_flow_graph import *
from visualizer import CFGVisualizer, DomTreeVisualizer
from printer import dom_tree_printer, frontier_printer

def main(args):
    # get options
    from_ssa = args.from_ssa
    to_ssa = args.to_ssa
    roundtrip = args.roundtrip
    const_fold = args.const_fold
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
    parser.add_argument('-from-ssa', dest='from_ssa',
                        default=False, action='store_true',
                        help='Convert SSA-form program to original')
    parser.add_argument('-to-ssa', dest='to_ssa',
                        default=False, action='store_true',
                        help='Convert program to SSA form')
    parser.add_argument('-roundtrip', dest='roundtrip',
                        default=False, action='store_true',
                        help='Convert program to SSA form then convert it back')
    parser.add_argument('-const-fold', dest='const_fold',
                        default=False, action='store_true',
                        help='Constant folding with global value numbering')
    parser.add_argument('-visualize', dest='visualize',
                        default=False, action='store_true',
                        help='visualize results')
    parser.add_argument('-f', dest='filename', 
                        action='store', type=str, help='json file')
    args = parser.parse_args()
    main(args)