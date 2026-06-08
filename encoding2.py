from pysat.formula import CNF
from pysat.card import *

def x(i):
    return i + 1

# o = ORDER, l = LENGTH
def encodingTwo(O, L):
    # assume n = ORDER = O

    cnf = CNF()
    
    # mark @ 0 for convention
    cnf.append([x(0)])

    # exactly n marks <==> sum of all x_i's is n
    baseVars = [x(i) for i in range(L + 1)]
    exactlyN = CardEnc.equals(lits=baseVars, bound=O, top_id=max(baseVars), encoding=EncType.totalizer)
    cnf.extend(exactlyN.clauses)

    # for tracking next unused id 
    offsetCounter = exactlyN.nv + 1

    deltaToID = {}
    for d in range(1, L + 1):
        for i in range(L + 1 - d):
            deltaToID[(i, d)] = offsetCounter
            offsetCounter += 1

    def delta(i, d):
        return deltaToID[(i, d)]

    baseClauses = len(cnf.clauses)

    #define deltas and enforce uniqueness
    # forall d in [1, L]
    for d in range(1, L + 1):
        deltaVars = []

        # forall starting index i where distance d will not go out of bounds
        for i in range(L + 1 - d):
            delta_id = delta(i, d)
            deltaVars.append(delta_id)

            # delta_id <==> x_i AND x_{i+d}
            # delta_id => x_i AND delta_id => x_{i+d} AND (x_i AND x_{i+d}) => delta_id 
            # (-delta_id OR x_i) AND (-delta_id OR x_{i+d}) AND (-x_i OR -x_{i+d} OR delta_id)
            cnf.append([-delta_id, x(i)])
            cnf.append([-delta_id, x(i + d)])
            cnf.append([delta_id, -x(i), -x(i + d)])

        # enforce uniqueness: for fixed d, at most one (AMO) delta_id can be true, forall i
        if deltaVars != []:
            amoDistance = CardEnc.atmost(lits=deltaVars, bound=1, top_id=(offsetCounter-1), encoding=EncType.bitwise)
            cnf.extend(amoDistance.clauses)
            offsetCounter = amoDistance.nv + 1


    return cnf, baseClauses

def getRulerTwo(model, O, L):
    ruler = []

    filteredVars = set(lit for lit in model if lit > 0)

    for i in range(L + 1):
        if x(i) in filteredVars:
            ruler.append(i)

    # print("Ruler:", ruler)
    # print("Valid?", verifyRuler(ruler))
    return ruler