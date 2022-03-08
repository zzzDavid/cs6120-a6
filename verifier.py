"""
This is a verifier of the dominator finding algorithm given a CFG.
It checks whether all possible paths to a target basic block pass
its dominators.
"""


class DominatorVerifier(object):

    def __init__(self, cfg, dom) -> None:
        """
        - cfg: dict(str, BasicBlock)
        - dom: dict(str, set(str))
        """
        self.cfg = cfg
        self.dom = dom
        
    def verify(self):
        for vertex, dominators in self.dom.items():
            for dominator in dominators:
                self.present = list()
                self.find_in_upstream(vertex, dominator)
                if not all(self.present):
                    return False
        return True

    def find_in_upstream(self, start, target):
        """
        Recursively find target vertex in "start"'s
        upstream vetices (DFS)
        """
        # self-relexive
        if start == target:
            self.present.append(True)
            return

        if len(self.cfg[start].pred) == 0:
            # we've reached the root node
            self.present.append(False)
            return
        # if target appears in upstream
        # mark found and stop looking
        if target in self.cfg[start].pred:
            self.present.append(True)
            return
        # if not, keep looking in upstream
        for pred in self.cfg[start].pred:
            self.find_in_upstream(pred, target)