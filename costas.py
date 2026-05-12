from pysat.formula import CNF
from pysat.card import *
import numpy as np
import matplotlib.pyplot as plt
import random, time 
from pysat.solvers import Minisat22

COSTAS_ARRAY_SIZE = 14

'''
Use the difference triangle construction:
If it has distinct non zero entries in each row, for each row, then the Costas array is valid

A sample 5x5 Costas Array (CA) would be like [5, 2, 4, 3, 1]

Let an arbitrary CA be [x1, x2, ... x{n-1}, xn]

We have to use a one-hot encoding for each of these xi's to pick the height
- so we'll need n^2 literals to represent the potential CA
- and then apply constraints
'''

'''
Constraints:
- Each column has one height
- Each height is used once 
- Costas Property through diff triangle 
'''

def x(i, j):
    return i * COSTAS_ARRAY_SIZE + j + 1

def exactlyOneHeightPerColumn(i):
    L = []
    for j in range(COSTAS_ARRAY_SIZE):
        L.append(x(i, j))

    cardConstraint = CardEnc.equals(L, bound=1, encoding=EncType.pairwise)
    return cardConstraint.clauses

def eachHeightUsedOnce(i):
    L = []
    for j in range(COSTAS_ARRAY_SIZE):
        L.append(x(j, i))

    cardConstraint = CardEnc.equals(L, bound=1, encoding=EncType.pairwise)
    return cardConstraint.clauses

def costasProperty():
    clauses = []

    # for each fixed row k, forall (u, v) in row k, d(u, k) != d(v, k) 
    # expand each out, set conjunction via assump, demorgans to get clause
    for k in range(1, COSTAS_ARRAY_SIZE):                       
        for u in range(COSTAS_ARRAY_SIZE - k):                  
            for v in range(u + 1, COSTAS_ARRAY_SIZE - k):      
                for z in range(-(COSTAS_ARRAY_SIZE - 1), COSTAS_ARRAY_SIZE):      
                    if z == 0:
                        continue
                    for a in range(COSTAS_ARRAY_SIZE):             
                        if a + z < 0 or a + z >= COSTAS_ARRAY_SIZE:
                            continue
                        for b in range(COSTAS_ARRAY_SIZE):
                            if a == b: continue    # maybe delete     
                            if b + z < 0 or b + z >= COSTAS_ARRAY_SIZE:
                                continue

                            clauses.append([
                                -x(u, a),
                                -x(u + k, a + z),
                                -x(v, b),
                                -x(v + k, b + z)
                            ])
    return clauses

def generateCostasCNF(baseOnly):
    cnf = CNF()

    # Column + Height constraints, respectively:
    for i in range(COSTAS_ARRAY_SIZE):
        cnf.extend(exactlyOneHeightPerColumn(i))
        cnf.extend(eachHeightUsedOnce(i))

    rowColClauseCount = len(cnf.clauses)

    if baseOnly: 
        return cnf

    # Costas prop via diff triangle constraints:
    cnf.extend(costasProperty())

    costasClauseCount = len(cnf.clauses) - rowColClauseCount

    print(f"Pct of row/col clauses to costas clauses: {rowColClauseCount / costasClauseCount * 100:.2f}%")

    return cnf

def printCostasArray(model):
    # use a O for positive lit, and a . for negative lit
    # new line every COSTAS_ARRAY_SIZE literals

    for i in range(COSTAS_ARRAY_SIZE):
        for j in range(COSTAS_ARRAY_SIZE):
            if x(i, j) in model:
                print("🟪", end="")
            else:
                print("⬜", end="")
        print()

def updateArray(model, weights):
    if len(model) != COSTAS_ARRAY_SIZE ** 2:
        print("Lengths don't match, cant update")
        return
    
    # i.e. -1, 2, -3, -4, 5, 6 etc
    model.sort(key=abs)
    for i in range(COSTAS_ARRAY_SIZE):
        for j in range(COSTAS_ARRAY_SIZE):
            index = x(i, j) - 1

            lit = model[index]
            if lit > 0:
                weights[index] += 1
            else:
                weights[index] -= 0.2
                
    return weights

def returnWeightArray():
    return [0.0] * (COSTAS_ARRAY_SIZE ** 2)

def normal():
    cnf = generateCostasCNF(False)
    print(f"\nCNF has {cnf.nv} variables and {len(cnf.clauses)} clauses")
    
    # solver = Cadical195()
    solver = Minisat22()
    solver.append_formula(cnf.clauses)

    start = time.perf_counter()
    print("\nSolving...")
    res = solver.solve()
    print("Solved.\n")
    end = time.perf_counter()

    print(f"Time to solve: {end - start} seconds")
    if res:
        print("SAT\n")
        model = solver.get_model()
        
        print("——" * COSTAS_ARRAY_SIZE)
        print("Printing Costas Array:\n")
        printCostasArray(model)
        print("——" * COSTAS_ARRAY_SIZE)
    else:
        print("UNSAT")

    return model

def findAllSolutions():
    cnf = generateCostasCNF(False)
    solver = Minisat22()
    solver.append_formula(cnf.clauses)

    allSatMap = [0] * (COSTAS_ARRAY_SIZE ** 2)

    solCount = 0
    while solver.solve():
        model = solver.get_model()
        solCount += 1

        for lit in model:
            index = abs(lit) - 1
            if lit > 0:
                allSatMap[index] += 1

        # add a negated clause to find distinct sol
        solver.add_clause([-lit for lit in model])

        if solCount % 200 == 0:
            print(f"Found {solCount} solutions so far...")

    # norm
    allSatMap = [val / solCount for val in allSatMap]

    return allSatMap

# THE FOLLOWING CODE WAS WRITTEN BY CHATGPT FOR MATPLOTLIB FOR VISUALIZATION
def plotAll(weights, solution):
    w = np.array(weights).reshape(COSTAS_ARRAY_SIZE, COSTAS_ARRAY_SIZE)
    s = np.array(solution).reshape(COSTAS_ARRAY_SIZE, COSTAS_ARRAY_SIZE)

    fig, axes = plt.subplots(1, 3, figsize=(18, 6))

    # weights heatmap
    im1 = axes[0].imshow(w, cmap="coolwarm", interpolation="nearest")
    axes[0].set_title("am i the thinker or the thought? (weights)")
    fig.colorbar(im1, ax=axes[0])

    # solution heatmap
    im2 = axes[1].imshow(s, cmap="Greens", interpolation="nearest")
    axes[1].set_title("Costas Solution(s) (real)")
    fig.colorbar(im2, ax=axes[1])

    # overlay
    axes[2].imshow(w, cmap="coolwarm", alpha=0.8)
    axes[2].imshow(s, cmap="Greens", alpha=0.35)
    axes[2].set_title("mix em up")

    for ax in axes:
        ax.set_xticks(range(COSTAS_ARRAY_SIZE))
        ax.set_yticks(range(COSTAS_ARRAY_SIZE))

    plt.tight_layout()
    plt.show()
# ====== CHATGPT CODE ENDS HERE =======



def costasMain():
    # normal SAT
    satSolution = normal()
    groundTruth = [1 if xi > 0 else 0 for xi in satSolution]

    # ALL SAT
    # groundTruth = findAllSolutions()

    weights = returnWeightArray()
    baseClauses = generateCostasCNF(True).clauses
    constraintClauses = costasProperty()
    numIterations = 20
    percentToTakeRandom = 80

    for _ in range(numIterations):
        solver = Minisat22()
        random.shuffle(baseClauses)
        solver.append_formula(baseClauses)

        # select random subset of constraint clauses
        sampledCostasClauses = random.sample(constraintClauses, int(len(constraintClauses) * percentToTakeRandom / 100))
        solver.append_formula(sampledCostasClauses)

        if solver.solve():
            model = solver.get_model()
            weights = updateArray(model, weights)

    weights = [val / numIterations for val in weights]
    plotAll(weights, groundTruth)
