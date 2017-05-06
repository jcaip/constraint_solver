"""
This is the backtracking search solver that uses a couple of heurestics in order to solve a constraint problem tree

Written by Jesse Cai
2017-05-05
"""
from igraph import *

class ConstraintSolver(object):

    def __init__(self, variables, consistency_type = 'arc'):
        self.csp = Graph()
        for var in variables:
            self.add_var(var, variables[var])

    def add_var(self, variable, domain):
        self.csp.add_vertex(name=variable, domain=domain)

    def add_constraint(self, constraint_func, *args):
        # if the number of args  
        if len(args) > 2:
            raise NotImplementedError('Have yet to deal with global constraints')
        self.csp.add_edge(*args, c_func=constraint_func)

    def add_constaints(self, list_of_constraints):
        for constaint in list_of_constraints:
            self.add_constaint(*constaint)

    #csp is a graph
    @classmethod
    def backtracking_search(cls, csp, assignment={}):
        if len(assignment.keys()) == len(csp.vs):
            return assignment

        var = cls.select_unassigned_var(assignment, csp)
        for value in cls.order_domain_values(var, assignment, csp):
            #add it into a possible assignment
            possible_assignment = assignment
            possible_assignment[var['name']] = value
            #check if assignment is possible
            if cls.consistency_checker(possible_assignment, csp):
                #if so commit, 
                assignment[var['name']] =  value
                new_csp = cls.inference(assignment, csp.copy())
                if new_csp:
                    #add inferences to assignment
                    result = cls.backtracking_search(new_csp, assignment)
                    if result:
                        return result
            assignment.pop(var['name'])
        return False

    #use the mininum remaining values heurestic
    #use the degree heurestic
    @staticmethod
    def select_unassigned_var(assignment, csp):
        current_best = None
        for vertex in csp.vs:
            if vertex['name'] not in assignment:
                if current_best:
                    if len(vertex['domain']) > len(current_best['domain']):
                        current_best = vertex
                    #if min remaining values are the same, then use degree heurestic
                    elif len(vertex['domain']) == len(current_best['domain']):
                        if csp.degree(vertex) > csp.degree(current_best):
                            current_best = vertex
                else:
                    current_best = vertex
        return current_best
    
    @classmethod
    def order_domain_values(cls, var, assignment, csp):
        value_range = []
        for value in var['domain']:
            assignment[var['name']] = value
            new_csp = cls.inference(assignment, csp.copy())
            if new_csp:
                vals_remaining = sum([len(d) for d in new_csp.vs['domain']])
                value_range.append((value, vals_remaining))
            del assignment[var['name']]
        value_range.sort(key=lambda x:x[1])
        return [x[0] for x in value_range]

    #this is just local consistency 
    @staticmethod
    def consistency_checker(assignment, csp):
        for edge in csp.es:
            src_name = csp.vs[edge.source]['name']
            target_name = csp.vs[edge.target]['name']
            if src_name in assignment and target_name in assignment:
                if not edge['c_func'](assignment[src_name], assignment[target_name]):
                    return False
        return True

    #inference using foward checking
    @classmethod
    def inference(cls, assignment, csp):
        neighboring_set = set()
        for set_val in assignment:
            neighboring_set.intersection_update(set(csp.neighbors(set_val)))

        for neighbor in neighboring_set:
            neighbor_name =  csp.vs[neighbor]['name']
            if neighbor_name not in assignment:
                for possible_value in csp.vs[neighbor]['domain']:
                    assignment[neighbor_name] = possible_value
                    if cls.consistency_checker(assignment, csp) == False:
                        csp.vs[neighbor]['domain'].remove(possible_value)
                    del assignment[neighbor_name]
                if csp.vs[neighbor]['domain'] == None:
                    return False
        return csp


test = {
    'california': ['r','g','b'],
    'oregon': ['r','g','b'],
    'nevada': ['r','g','b'],
    'washington': ['r','g','b'],
    'arizona': ['r','g','b']
}

# constraint retrusn true if valid, false otherwise
def not_equal_constraint(a, b):
    return a != b

mysolver = ConstraintSolver(test)
mysolver.add_constraint(not_equal_constraint, 'california', 'oregon')
mysolver.add_constraint(not_equal_constraint, 'california', 'nevada')
mysolver.add_constraint(not_equal_constraint, 'oregon', 'washington')
mysolver.add_constraint(not_equal_constraint, 'nevada', 'arizona')
mysolver.add_constraint(not_equal_constraint, 'california', 'arizona')

print(mysolver.backtracking_search(mysolver.csp))
