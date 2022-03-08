from graphviz import Digraph

# Text format pretty-printer.

def type_to_str(type):
    if isinstance(type, dict):
        assert len(type) == 1
        key, value = next(iter(type.items()))
        return '{}<{}>'.format(key, type_to_str(value))
    else:
        return type


def instr_to_string(instr):
    if instr['op'] == 'const':
        tyann = ': {}'.format(type_to_str(instr['type'])) \
            if 'type' in instr else ''
        return '{}{} = const {}'.format(
            instr['dest'],
            tyann,
            str(instr['value']).lower(),
        )
    else:
        rhs = instr['op']
        if instr.get('funcs'):
            rhs += ' {}'.format(' '.join(
                '@{}'.format(f) for f in instr['funcs']
            ))
        if instr.get('args'):
            rhs += ' {}'.format(' '.join(instr['args']))
        if instr.get('labels'):
            rhs += ' {}'.format(' '.join(
                '.{}'.format(f) for f in instr['labels']
            ))
        if 'dest' in instr:
            tyann = ': {}'.format(type_to_str(instr['type'])) \
                if 'type' in instr else ''
            return '{}{} = {}'.format(
                instr['dest'],
                tyann,
                rhs,
            )
        else:
            return rhs


def print_instr(instr):
    return '  {};'.format(instr_to_string(instr))


class CFGVisualizer(object):
    """
    - cfg: dict(str, BasicBlock)
    """
    def __init__(self, cfg, name) -> None:
        self.cfg = cfg
        self.dot = Digraph(name, node_attr={'shape': 'rectangle'})
        self.build()        

    def build(self):
        # build nodes
        for label, bb in self.cfg.items():
            instr_str = '.' + label + ":\l"
            for instr in bb.instrs:
                if 'op' not in instr: continue
                instr_str += "  " + print_instr(instr) + "\l"
            self.dot.node(label, instr_str)
        # build edges
        for label, bb in self.cfg.items():
            for succ in bb.succ:
                self.dot.edge(label, succ)
    
    def show(self):
        self.dot.render(view=True)
    
    def save(self, filename):
        self.dot.render(view=False, format='pdf', filename=filename)

class DomTreeVisualizer(object):
    """
    - domtree: dict(str, Node)
    """
    def __init__(self, dom_tree, name):
        self.dom_tree = dom_tree
        self.dot = Digraph(name)
        self.build()

    def build(self):
        # build nodes
        for vertex in self.dom_tree.keys():
            self.dot.node(vertex, vertex)
        # build edges
        for vertex, node in self.dom_tree.items():
            for succ in node.succs:
                self.dot.edge(vertex, succ)
    
    def show(self):
        self.dot.render(view=True)

    def save(self, filename):
        self.dot.render(view=False, format='pdf', filename=filename)