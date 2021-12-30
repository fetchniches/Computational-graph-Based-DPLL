from cg import Node, NodeType
from function import op_and, op_or, op_identity, Operator


# TODO: store numebr of True atoms
class Formula(Node): ...
class Formula(Node):
    ID = 1
    def __init__(self, nt: NodeType = NodeType.LeafNode, op: Operator = op_identity, sformat: str = "A"):
        super().__init__(nt, op)
        self.invert = None
        self.assigned = False
        self.sid = f"{sformat}{Formula.ID}"
        self.id = Formula.ID
        Formula.ID += 1
        self.atoms = []
        self.forms = None
        self.length = 1
        self.visited = None 
        self.true_atoms = 0

    def __or__(self, f: Formula):
        if self.nt == NodeType.LeafNode and f.nt == NodeType.LeafNode:
            form = Formula(NodeType.BranchNode, op_or)
            if self != f:
                form.prev_nodes = [self, f]
                f.next_nodes.append(form)
                form.length = 2
            else:
                form.prev_nodes = [self]
                form.length = 1
            self.next_nodes.append(form)      
        else:
            exists = False
            for fnn in f.next_nodes:
                if self is fnn: 
                    exists = True
                    break
            if not exists:
                self.prev_nodes.append(f)
                f.next_nodes.append(self)
                self.length += 1
            form = self
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
        if self.value: 
            return 0
        else: return self.length 

    def __getitem__(self, index):
        if index != 0:
            raise IndexError('only zero indice is supported.')
        for atom in self.prev_nodes:
            if not atom.isAssigned():
                return atom
        raise Exception('length doesn\'t match to formlua.')

    def __str__(self): 
        if self.nt == NodeType.BranchNode:
            self.sid = f"{self.prev_nodes[0]}"
            for prev in self.prev_nodes[1:]:
                self.sid = f"{self.sid} {self.op} {prev}"
            self.sid = f"({self.sid})"
        return self.sid

    def fuzzy(self, invert: bool = False):
        """将该节点状态设置为FUZZY，在进一步的compute()中则会更新"""
        if self.nt == NodeType.LeafNode:
            if self.value:
                for form in Formula.getFormulas(self):
                    form.true_atoms -= 1
                    if not form.true_atoms: form.sat(False)
            self.update(False)
        self.value = None
        if not invert and self.invert is not None:
            self.invert.fuzzy(True)

    def sat(self, sat: bool = True): 
        """将该节点状态设置SAT或UNSAT"""
        if not self.value and sat: # not sat -> sat
            self.value = sat
            return True
        else: 
            self.value = sat
            return False

    def update(self, assigned: bool = True):
        """更新当前节点状态并传递给其所在的公式"""
        forms = Formula.getFormulas(self)
        if assigned and not self.assigned:
            forms = Formula.getFormulas(self)
            for f in forms:
                f.length -= 1
        elif not assigned and self.assigned:
            forms = Formula.getFormulas(self)
            for f in forms:
                f.length += 1
            self.value = None
        self.assigned = assigned

    def assign(self, value: int, invert: bool = False): 
        """为节点指派一个值"""
        if self.nt != NodeType.LeafNode:
            raise RuntimeError('Failed to assign value to non-leaf node.')
        if value and not self.value:
            for form in Formula.getFormulas(self):
                form.sat() 
                form.true_atoms += 1
        elif not value and self.value:
            for form in Formula.getFormulas(self):
                form.true_atoms -= 1
                if not form.true_atoms:
                    form.sat(False)
        self.value = value != 0
        self.update()
        if not invert and self.invert is not None:
            self.invert.assign(not value, True)
    
    def isSatisfied(self): 
        """是否SAT"""
        if self.value is not None:
            return self.value
        else:
            self.value = self.compute()
            if self.value == 1:
                return True
            else: return False
    
    def isAssigned(self):
        """是否已经指派过值"""
        return self.assigned

    def compute(self):
        """返回 0, 1, None, 同时更新SAT情况"""
        self.value = 0
        for node in self.prev_nodes:
            if node.value == 1:
                self.value = 1
                break
            if node.value is None:
                self.fuzzy()
        if self.value == 0: self.sat(False)
        return self.value

    @staticmethod
    def getFormulas(formula: Formula):
        """利用原子公式获取公式"""
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
    def isValidity(formula):
        """
        用于判断某一公式是否未永真式，利用visited属性当前指向遍历的公式ID，
        这样只需要遍历一遍即可判断是否A与~A均出现
        """
        for item in formula.prev_nodes:
            if not item.isAssigned() and item.invert is not None and item.invert.visited == formula.id:
                return True
        return False
    
    # def __del__(self): 
    #     print('freed node :', self.sid))

if __name__ == "__main__":
    fs = [Formula() for i in range(3)]
    # d = fs[2] | fs[2] | (fs[1] & fs[0]) | (fs[2] & fs[2])
    c = fs[0] | fs[1] | fs[2] | fs[1] | fs[2]
    # c = fs[1] & ~fs[0]
    # print(d)
    # for i in Formula.getFormulas(fs[0]): print(i)
    # print(d)
    