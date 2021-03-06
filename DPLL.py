import time
from typing import List
from cg import NodeType
from formula import Formula
import os
from pathlib import Path
import sys
from function import op_or

sys.setrecursionlimit(3000)

def compute_result_on_cnf(forms):
    ret = 1
    for form in forms:
        res = form.compute()
        if res is None:
            return False
        ret &= res
    return ret

class CNFParser:

    def __init__(self, cnf_folders: os.PathLike, encoding: str = "utf-8"):
        self.e = encoding
        if not os.path.exists(cnf_folders):
            raise FileExistsError(f"{Path(cnf_folders).absolute()} doesn't exist.")
        self.cnfs = []
        for cnf in os.listdir(cnf_folders):
            if cnf.lower().endswith(".cnf"):
                self.cnfs.append(os.path.join(cnf_folders, cnf))

    def __parse_single_file(self, file: os.PathLike):
        with open(file=file, mode="r", encoding=self.e) as cnf:
            lines = cnf.readlines()

        clauses = []
        vars = []
        for id in range(len(lines)):
            if lines[id].startswith("c"):
                continue
            elif lines[id].startswith("p"):
                infos = lines[id].split(" ")
                vars = [Formula() for i in range(int(infos[2]))]
                print(f"Current File : {file}\nBool Variable Number : {infos[2]}, Clause Number : {infos[3]}")
            else:
                clause = Formula(NodeType.BranchNode, op=op_or)
                vars_in_int = map(lambda s: int(s), lines[id].split(" "))
                for id, vi in enumerate(vars_in_int):
                    if vi == 0: break
                    if id == 0: 
                        v = vars[vi-1] if vi > 0 else ~vars[-vi-1]
                        clause.prev_nodes.append(v)
                        v.next_nodes.append(clause)
                    else: clause |= vars[vi-1] if vi > 0 else ~vars[-vi-1]
                    clause |= vars[vi-1] if vi > 0 else ~vars[-vi-1]
                clauses.append(clause)
        return clauses, vars

    def __len__(self):
        return len(self.cnfs)
    
    def __getitem__(self, index):
        return self.__parse_single_file(self.cnfs[index])
        
class DPLL:

    def __init__(self, form: List[Formula], vars: List[Formula]):
        self.forms = form
        self.vars = vars
        self.branches = []

    def rule1(self):
        """???????????????"""
        used = False
        single_atoms = []
        single_forms = []
        for f in self.forms:
            # len ??????????????????????????????????????????????????????????????????SAT?????????0
            if len(f) == 1:
                used = True
                single_atoms.append(f[0])
                for formula in Formula.getFormulas(f[0]):
                    if not formula.isSatisfied():
                        single_forms.append(formula)
                f[0].assign(1)
        return used, single_atoms, single_forms
    
    def rule2(self):
        """???????????????"""
        used = False
        for var in self.vars:
            # getFormulas?????????????????????????????????
            forms = Formula.getFormulas(var)
            # ~A?????????
            if var.invert is None:
                used = True
                var.assign(1)
                [formula.sat() for formula in forms]
            # ??????~A????????????A???????????????????????????????????????~A 
            elif not forms:
                used = True
                (~var).assign(1)
                [formula.sat() for formula in Formula.getFormulas(~var)]
        return used

    def rule3(self):
        """???????????????"""
        used = False
        for form in self.forms:
            store_true = Formula.isValidity(form)
            if store_true: 
                used = True
                form.sat()
        return used

    def rule4(self):
        """????????????"""
        for var in self.vars:
            if not var.isAssigned():
                var.assign(0)
                # ????????????
                self.branches.append(var)
                return True
        return False
        
    def isSAT(self):
        for f in self.forms:
            if not f.isSatisfied():
                return False
        return True
    
    def isAssigned(self):
        for var in self.vars:
            if not var.isAssigned():
                return False
        return True
    
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
                        # ??????rule1??????
                        state = rule1_state[-1]
                        branch.fuzzy()
                        for single_atom in state[0]:
                            single_atom.fuzzy()
                        for single_form in state[1]:
                            single_form.fuzzy()
                        rule1_state.pop()
                        self.branches.pop()
                    else: 
                        branch.assign(1)
                        state = rule1_state[-1]
                        for single_atom in state[0]:
                            single_atom.fuzzy()
                        for single_form in state[1]:
                            single_form.fuzzy()
                        rule1_state.pop()
                        # ????????????0?????????
                        temp_atoms = []
                        temp_forms = []
                        while True: 
                            ret, temp_A, temp_F = self.rule1()
                            if not ret: break
                            temp_atoms += temp_A
                            temp_forms += temp_F
                        rule1_state.append((temp_atoms, temp_forms))
                        break
                if not self.branches:
                    return False
            # normal rule
            if self.rule4():
                temp_atoms = []
                temp_forms = []
                while True: 
                    ret, temp_A, temp_F = self.rule1()
                    if not ret: break
                    temp_atoms += temp_A
                    temp_forms += temp_F
                rule1_state.append((temp_atoms, temp_forms))
        return True

  
if __name__ == "__main__":
    cnfs = CNFParser("./randn_cnfs")
    preprocess = []
    solves = []
    for i in range(len(cnfs)):
        s = time.time()
        print('-'*25)
        forms, vars = cnfs[i]
        print(f"Preprocess Time : {1e3*(time.time()-s):.4f} ms")
        solver = DPLL(forms, vars)
        s = time.time()
        
        print("SAT result :",solver.solve())
        print(f"solved in {1e3*(time.time()-s):.4f}ms")
        ret = compute_result_on_cnf(forms)
        print("compute result :", ret)
        # if ret:
        #     print("vars assign : ")
        #     for var in vars: 
        #         print(f"{var} - {'Any' if var.value is None else var.value}\t", end='')