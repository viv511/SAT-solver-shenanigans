from pysat.formula import CNF
from pysat.card import *

def x(i, v, L):
    return i * (L + 1) + v + 1

def markFirst(L):
    return [[x(0, 0, L)]]

def oneValuePerMark(i, L):
    list_l = []
    for v in range(L + 1):
        list_l.append(x(i, v, L))

    cardConstraint = CardEnc.equals(list_l, bound=1, encoding=EncType.pairwise)
    return cardConstraint.clauses

def sortedMarks(O, L):
    c = []
    for i in range(1, O):
        for u in range(L + 1):
            for v in range(0, u + 1):
                c.append([-x(i - 1, u, L), -x(i, v, L)])

    return c

# define d (i,j, delta) as distance from i and j being delta
def d(i, j, delta, O, L):
    offset = O * (L + 1)
    return offset + (i * O * (L + 1)) + (j * (L + 1)) + delta + 1

def distinctDiffs(O, L):
    # DEFINE DISTANCES
    # if mark i is @ u and mark j is @ v, then d(i,j,v-u) is true
    # x(i,u) and x(j,v) => d(i,j,v-u)
    # further, (a ^ b => c) <===> not a or not b or c!

    c = []
    for i in range(O):
        for j in range(i + 1, O):
            for u in range(L + 1):
                for v in range(u + 1, L + 1):
                    c.append([-x(i, u, L), -x(j, v, L), d(i, j, v - u, O, L)])
    # ENFORCE DISTINCTNESS
    # idea: for all pairwise distances, use AMO (at most one) so each distance USED is UNIQUE

    for delta in range(1, L + 1):
        list_l = []

        for i in range(O):
            for j in range(i + 1, O):
                list_l.append(d(i, j, delta, O, L))

        # AMO if theres more than 1 possible
        if len(list_l) > 1:
            cardConstraint = CardEnc.atmost(list_l, bound=1, encoding=EncType.pairwise)
            c.extend(cardConstraint.clauses)

    return c

'''
encoding idea:
- increasing marks
- a_1 = 0 (wlog)
- a_n < L (in other words, we add a maximum constraint to the length)
- pairwise distinctness in differences, via additional differnce variables
'''
def encodingOne(O, L):
    cnf = CNF()

    cnf.extend(markFirst(L))
    
    for i in range(1, O):
        cnf.extend(oneValuePerMark(i, L))

    cnf.extend(sortedMarks(O, L))

    necessaryClauses = len(cnf.clauses)

    cnf.extend(distinctDiffs(O, L))

    return cnf, necessaryClauses

def getRulerOne(model, O, L):
    ruler = [0] * O

    filteredVars = set(lit for lit in model if lit > 0)

    for i in range(O):
        for v in range(L + 1):
            if x(i, v, L) in filteredVars:
                ruler[i] = v

    # print("Ruler:", ruler)
    # print("Valid?", verifyRuler(ruler))
    return ruler