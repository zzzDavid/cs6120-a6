TERMINATORS = ['jmp', 'ret', 'br']

class BasicBlock(object):
    def __init__(self, block):
        self.instrs = block
        self.pred = []
        self.succ = []

class CFG(object):
    """
    Give each block succ and pred 
    """
    def __init__(self, blocks, reverse=False):
        self.labels = list()
        self.blocks = blocks
        self.cfg = dict()
        self.reverse = reverse
        self.build_cfg()
    
    def build_cfg(self):
        # convert blocks from a list to a dictionary
        for block in self.blocks:
            # go through all blocks
            # build a list of Blocks
            bb = BasicBlock(block)
            label = "start"
            if "label" in block[0]:
                label = block[0]['label']
            self.cfg[label] = bb
            self.labels.append(label)

        # add succ and pred to the basic blocks
        labels = list(self.cfg.keys())
        for idx, label in enumerate(labels):
            bb = self.cfg[label]
            # check the ternimator instr
            op = bb.instrs[-1]['op']
            if op not in TERMINATORS:
                # natural terminator
                if idx == len(labels) -1 :
                    # end of function
                    self.cfg[label].instrs.append({'op': 'ret', 'args': []})
                    continue
                else:
                    jmp_target = self.cfg[labels[idx + 1]].instrs[0]['label']
                    self.cfg[label].instrs.append({'op': 'jmp', 'labels': [jmp_target]})
                    if self.reverse:
                        self.cfg[label].pred.append(jmp_target)
                        self.cfg[jmp_target].succ.append(label)
                    else:
                        self.cfg[label].succ.append(jmp_target)
                        self.cfg[jmp_target].pred.append(label)
            elif op == "jmp":
                jmp_target = bb.instrs[-1]['labels'][0]
                if self.reverse:
                    self.cfg[label].pred.append(jmp_target)
                    self.cfg[jmp_target].succ.append(label)
                else:
                    self.cfg[label].succ.append(jmp_target)
                    self.cfg[jmp_target].pred.append(label)
            elif op == "br":
                br_targets = bb.instrs[-1]['labels']
                for target in br_targets:
                    if self.reverse:
                        self.cfg[label].pred.append(target)
                        self.cfg[target].succ.append(label)
                    else:
                        self.cfg[label].succ.append(target)
                        self.cfg[target].pred.append(label)

    def gen_instrs(self):
        instrs = list()
        for label in self.labels:
            if 'label' not in self.cfg[label].instrs[0]:
                instrs.append({'label' : label})
            instrs.extend(self.cfg[label].instrs)
        return instrs