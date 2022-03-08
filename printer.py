from collections import OrderedDict
import json

def dom_tree_printer(dom_tree):
    """
    - dom_tree: dict(str, node)
    """
    res = OrderedDict()
    keys_sorted = list(dom_tree.keys())
    keys_sorted.sort()
    for vertex in keys_sorted:
        l = list(dom_tree[vertex].succs)
        l.sort()
        res[vertex] = l
    print(json.dumps(res, indent=2))

def frontier_printer(frontier):
    """
    - frontier: dict(str, set(str))
    """
    res = OrderedDict()
    keys_sorted = list(frontier.keys())
    keys_sorted.sort()
    for vertex in keys_sorted:
        l = list(frontier[vertex])
        l.sort()
        res[vertex] = l
    print(json.dumps(res, indent=2))