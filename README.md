# Computational-graph-Based-DPLL

A implementation of DPLL algorithm based on computational graph.

## File Structure

- `cg.py` - implementation of computational graph node.
- `formula.py`  -  it simulates the behaviours of a formula and use to construct a graph.
- `function.py` - bit operation.
- `DPLL.py` - includes file parsing and the implemenmtation of DPLL algorithm.

## Details

### Node

```python
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

    def compute(self): ...
```

​	Each node object store its node types, operator, previous nodes (nodes to it), next nodes (nodes from it) and value. The method `compute()` used to recursively compute every nodes connecting to this node, namely `self` object, the previous nodes used as inputs for this node.

### Formula(Node)

```python
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
...
```

​	The `Formula` class inherits the base class `Node`, and override methods like `compute(self)`, `__or__(self)`  , `__invert__(self)` to record the data flow and improve the performance of the calculation.

```python
def __or__(self, f: Formula):
    # check if they are two leaf nodes, if so create new node
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
     # if not use the current node and connect other node to it.
        else:
            # check if this node is repeated.
            exists = False
            for fnn in f.next_nodes:
                if self is fnn: 
                    exists = True
                    break
            # if not then connects it
            if not exists:
                self.prev_nodes.append(f)
                f.next_nodes.append(self)
                self.length += 1
            form = self
        return form
```

​	This is the  override operator `|`, because this is sepecific to CNF formula, so the optimization could be very simple as above.

```python
def __invert__(self):
    if self.invert is None:
        form = Formula(NodeType.LeafNode)
        form.sid = f'(~{self.sid})'
        self.invert = form
        form.invert = self
    else: form = self.invert
    return form
```

​	This is the override operator `~`, which used to get the inverted nodes, this operation do not include in data flow graph, because this would add more if-else in codes.

​	There are basic three states for a `Formula`, `SAT`, `UNSAT` and `FUZZY`, this can be accessed by method `isSatisfied()->bool` it returns true only if the state is `SAT`,  this state is actually defined by its attribute `value` to determine the state. 

```python
    def assign(self, value: int): 
        if self.nt != NodeType.LeafNode:
            raise RuntimeError('Failed to assign value to non-leaf node.')
        if self.invert is not None:
            inv = self.invert
            inv.update()
            inv.value = value == 0
        if self.value:
            [form.sat() for form in Formula.getFormulas(self)]
        self.update()
        self.value = value != 0
        
    def compute(self):
        self.value = 0
        for node in self.prev_nodes:
            if node.value == 1:
                self.value = 1
                break
            if node.value is None:
                self.fuzzy()
        if self.value == 0: self.sat(False)
        return self.value
```

​	In the DPLL process, if some formula's value needs to assign, method `assign(self, value)` can be used, if it is assigned value `1`, the method would transform all the connected formulas state to `SAT`, which is pretty useful when apply the `rule4`.  And there is also method `fuzzy()` to set current atoms or formula value to None, so when the method `compute()` is invoked, it will check if it is in `FUZZY` state, if so it then computes recursively, if not it directly return value according to the state.

### DPLL

```python
def solve(self):
    self.rule2()
    self.rule3()
    rule1_state = []
    while not self.isSAT():
        if self.isAssigned():
            # stack traceback
            while self.branches:
                branch = self.branches[-1]
                if branch.value == 1:
                    branch.fuzzy()
                    # resotre state modified by rule1
                    state = rule1_state[-1]
                    for single_atom in state[0]: 
                        single_atom.fuzzy()
                    for single_form in state[1]:
                        single_form.fuzzy()
                    rule1_state.pop()
                    self.branches.pop()
                else: 
                    branch.assign(1)
                    break
            if not self.branches:
                return False
        # normal rule
        self.rule4()
        temp_atoms = []
        temp_forms = []
        while True: 
            ret, temp_A, temp_F = self.rule1()
            if not ret: break
            temp_atoms += temp_A
            temp_forms += temp_F
        rule1_state.append((temp_atoms, temp_forms))
    return True
```

​	In DPLL process, we use relu1_state to trace back to the state modified by `rule1`, and `branches` to trace the assignment of `rule4`

