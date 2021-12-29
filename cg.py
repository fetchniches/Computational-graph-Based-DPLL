from enum import Enum
from typing import List
from function import Operator

class NodeType(Enum):
    LeafNode = 1
    BranchNode = 2
    
class Node(object):
    
    def __init__(self, nt: NodeType, op: Operator = None):
        super().__init__()
        self.nt = nt
        self.op = op
        self.prev_nodes: List[Node] = []
        self.next_nodes: List[Node] = []
        self.value = None

    def compute(self):
        if self.nt == NodeType.LeafNode:
            if self.value is None:
                raise RuntimeError("Unkonw value appears in leaf node.")
        elif self.nt == NodeType.BranchNode:
            for node in self.prev_nodes:
                node.compute()
            self.setValue(self.op(*self.prev_nodes))
        return self.value
    

