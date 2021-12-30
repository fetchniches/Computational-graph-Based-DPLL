from typing import Union
from cg import *
from function import op_and, op_or, op_identity


class Formula(Node): ...
class Formula(Node):
    ID = 1
    def __init__(self, nt: NodeType = NodeType.LeafNode, op: Operator = op_identity, sformat: str = "A"):
        super().__init__(nt, op)
        self.satisfied = False
        self.invert = None
        self.fixed = False
        self.sid = f"{sformat}{Formula.ID}"
        self.id = Formula.ID
        Formula.ID += 1
        self.atoms = []
        self.forms = None
        self.length = 0
        self.visited = None
        self.store_true = None
        
    def setValue(self, x):
        self.value = x != 0
        if self.invert is not None:
            self.invert.value = x == 0

    def __add_ops(self, op: Operator, f: Formula):
        form = Formula(NodeType.BranchNode, op)
        for node in [self, f]:
            if node.op.name == op.name:
                form.prev_nodes += node.prev_nodes
                [(pn.next_nodes.append(form), pn.next_nodes.remove(node)) for pn in node.prev_nodes]
            else:
                form.prev_nodes.append(node)
                node.next_nodes.append(form)

        return form

    def __or__(self, f):
        form = self.__add_ops(op_or, f)
        form.sid = f"({self.sid} | {f.sid})"
        return form
        
    def __and__(self, f):
        form = self.__add_ops(op_and, f)
        form.sid = f"({self.sid} & {f.sid})"
        return form
        
    def __invert__(self):
        if self.invert is None:
            form = Formula(NodeType.LeafNode)
            form.sid = f'(~{self.sid})'
            self.invert = form
            form.invert = self
        else: form = self.invert
        return form

    def __len__(self):
        if self.satisfied: 
            return 0
        else:   
            return self.length

    def __getitem__(self, index):
        return Formula.backward(self, visit=Formula.__visit_item)[index]
    
    @staticmethod
    def __visit_item(node, result: Union[List, None]):
        if result is None: result = []
        if node.nt == NodeType.LeafNode and not node.isFixed() and node.invert != None: 
            result.append(node)
        return result
            
    @staticmethod
    def backward(node: Node, visit, result: Any = None):
        for n in node.prev_nodes:
            result = Formula.backward(n, visit, result)
        return visit(node, result)

    def __str__(self): 
        if self.nt == NodeType.BranchNode:
            self.sid = f"{self.prev_nodes[0]}"
            for prev in self.prev_nodes[1:]:
                self.sid = f"{self.sid} {self.op} {prev}"
            self.sid = f"({self.sid})"
        return self.sid


    def sat(self, sat: bool = True): self.satisfied = sat

    def fix(self, fix: bool = True): 
        forms = Formula.getFormulas(self)
        if fix and not self.fixed:
            forms = Formula.getFormulas(self)
            for f in forms:
                f.length -= 1
        elif not fix and self.fixed:
            forms = Formula.getFormulas(self)
            for f in forms:
                f.length += 1
        self.fixed = fix

    def assign(self, value: int): 
        if self.nt != NodeType.LeafNode:
            raise RuntimeError('Failed to assign value to non-leaf node.')
        if self.invert is not None:
            inv = self.invert
            inv.fix()
            inv.value = value == 0
        self.fix()
        self.value = value != 0
    
    def isSatisfied(self): 
        if self.satisfied:
            return self.satisfied
        else:
            try:
                return self.compute()
            except RuntimeError:
                return False
    
    def isFixed(self): return self.fixed

    @staticmethod
    def getFormulas(formula):
        def inner(formula: Formula):
            if not formula.next_nodes: 
                # ignore atom
                if formula.prev_nodes: return [formula]
                else: return []
            nodes = []
            # ignore single node
            for node in formula.next_nodes:
                nodes += inner(node)
            return nodes
        if formula.forms is None:
            formula.forms = set(inner(formula))
        return formula.forms

    @staticmethod
    def getAtoms(formula):
        def inner(node):
            node.visited = formula.id
            if node.nt == NodeType.LeafNode:
                formula.atoms.append(node)
                formula.length += 1
                if node.invert is not None:
                    return node.invert.visited == node.visited
                else: return False
            ret = False
            for n in node.prev_nodes:
                ret |= inner(n)
            return ret
        if formula.store_true is None:
            formula.store_true = inner(formula)
        return formula.store_true
    
    # def __del__(self): 
    #     print('freed node :', self.sid)

            

if __name__ == "__main__":
    fs = [Formula() for i in range(3)]
    d = fs[2] | fs[2] | (fs[1] & fs[0]) | (fs[2] & fs[2])
    c = fs[0] | fs[1] | fs[2] & fs[1]
    # c = fs[1] & ~fs[0]
    # print(d)
    print(d)
    # for node in d.prev_nodes: print(node)
    # for i in Formula.getFormulas(fs[0]): print(i)
    # print(d)
    