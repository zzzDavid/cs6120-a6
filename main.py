import argparse
import json
import copy
import sys

from basic_block import form_basic_blocks
from control_flow_graph import *
from visualizer import CFGVisualizer, DomTreeVisualizer
from to_ssa import cfg_to_ssa

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
        cfg_object = CFG(blocks)
        cfg = cfg_object.cfg
        cfg_to_ssa(cfg)
        if viz:        
            cfg_visualizer = CFGVisualizer(cfg, func['name'] + '-cfg')
            cfg_visualizer.show()

        # put updated instrs back to func
        func['instrs'] = cfg_object.gen_instrs()
    
    print(json.dumps(prog, indent=2))


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