
def _identity(node: object):
    return node.value

def _or(node: object, *args):
    ret = node.value
    for arg in args:
        ret |= arg.value
    return ret

def _and(node: object, *args):
    ret = node.value
    for arg in args:
        ret &= arg.value
    return ret

class Operator(object):
    
    def __init__(self, func: callable, name: str = '', _str: str = ''):
        super().__init__()
        self.func = func
        self.name = name
        self.str = _str
    
    def __call__(self, node, *args):
        return self.func(node, *args)
    
    def __str__(self):
        return self.str

class Identity(Operator):
    
    def __init__(self):
        super().__init__(_identity, 'identity', '')
        
class And(Operator):
    
    def __init__(self):
        super().__init__(_and, 'and', '&')

class Or(Operator):
    
    def __init__(self):
        super().__init__(_or, 'or', '|')

op_or = Or()
op_and = And()
op_identity = Identity()

if __name__ == "__main__":
    print(op_identity.name)
    