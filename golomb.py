from matplotlib import colors
from pysat.formula import CNF
from pysat.card import *
from pysat.solvers import Minisat22
import numpy as np
import matplotlib.pyplot as plt
import time, random

GOLOMB_RULER_SIZE = 11
UPPER_L = 75

def x(i, v):
    return i * (UPPER_L + 1) + v + 1

def markFirst():
    return [[x(0, 0)]]

def oneValuePerMark(i):
    L = []
    for v in range(UPPER_L + 1):
        L.append(x(i, v))

    cardConstraint = CardEnc.equals(L, bound=1, encoding=EncType.pairwise)
    return cardConstraint.clauses

def sortedMarks():
    c = []
    for i in range(1, GOLOMB_RULER_SIZE):
        for u in range(UPPER_L + 1):
            for v in range(0, u + 1):
                c.append([-x(i - 1, u), -x(i, v)])

    return c

# define d (i,j, delta) as distance from i and j being delta
def d(i, j, delta):
    offset = GOLOMB_RULER_SIZE * (UPPER_L + 1)
    return offset + (i * GOLOMB_RULER_SIZE * (UPPER_L + 1)) + (j * (UPPER_L + 1)) + delta + 1

def distinctDiffs():
    # DEFINE DISTANCES
    # if mark i is @ u and mark j is @ v, then d(i,j,v-u) is true
    # x(i,u) and x(j,v) => d(i,j,v-u)
    # further, (a ^ b => c) <===> not a or not b or c!

    c = []
    for i in range(GOLOMB_RULER_SIZE):
        for j in range(i + 1, GOLOMB_RULER_SIZE):
            for u in range(UPPER_L + 1):
                for v in range(u + 1, UPPER_L + 1):
                    c.append([-x(i, u), -x(j, v), d(i, j, v - u)])

    # ENFORCE DISTINCTNESS
    # idea: for all pairwise distances, use AMO (at most one) so each distance USED is UNIQUE

    for delta in range(1, UPPER_L + 1):
        L = []

        for i in range(GOLOMB_RULER_SIZE):
            for j in range(i + 1, GOLOMB_RULER_SIZE):
                L.append(d(i, j, delta))

        # AMO if theres more than 1 possible
        if len(L) > 1:
            cardConstraint = CardEnc.atmost(L, bound=1, encoding=EncType.pairwise)
            c.extend(cardConstraint.clauses)

    return c

'''
encoding idea:
- increasing marks
- a_1 = 0 (wlog)
- a_n < L (in other words, we add a maximum constraint to the length)
- pairwise distinctness in differences, via additional differnce variables
'''
def encodeRuler():
    cnf = CNF()

    cnf.extend(markFirst())
    for i in range(1, GOLOMB_RULER_SIZE):
        cnf.extend(oneValuePerMark(i))

    cnf.extend(sortedMarks())

    necessaryClauses = len(cnf.clauses)

    cnf.extend(distinctDiffs())

    return cnf, necessaryClauses

def displayRuler(model):
    ruler = [0] * GOLOMB_RULER_SIZE

    filteredVars = set(lit for lit in model if lit > 0)

    for i in range(GOLOMB_RULER_SIZE):
        for v in range(UPPER_L + 1):
            if x(i, v) in filteredVars:
                ruler[i] = v

    # print("Ruler:", ruler)
    # print("Valid?", verifyRuler(ruler))
    return ruler

def verifyRuler(ruler):
    dists = set()
    for i in range(len(ruler)):
        for j in range(i + 1, len(ruler)):
            d = abs(ruler[i] - ruler[j])
            if d in dists:
                return False
            dists.add(d)
    return True

def golombSAT(F, prettyPrint):
    solver = Minisat22()
    solver.append_formula(F.clauses)

    start = time.perf_counter()

    if prettyPrint:
        print("\nSolving...")

    res = solver.solve()
    end = time.perf_counter()

    if prettyPrint:
        print("Solved.\n")
        print(f"Time to solve: {end - start} seconds")
    
    if res:
        if prettyPrint:
            print("SAT\n")
        model = solver.get_model()
        return displayRuler(model), end - start
    else:
        if prettyPrint:
            print("UNSAT")
    raise Exception("shouldn't be here")

def rulerToBoard(ruler):
    b = [0.0] * (UPPER_L + 1)
    for r in ruler:
        b[r] = 1.0
    return b

def displayBoard(scoreboard):
    plt.figure(figsize=(20, 3))

    vmin = np.min(scoreboard)
    vmax = np.max(scoreboard)

    if vmin < 0 < vmax:
        norm = colors.TwoSlopeNorm(
            vmin=vmin,
            vcenter=0.0,
            vmax=vmax
        )
    else:
        norm = None

    plt.imshow([scoreboard], cmap='bwr', aspect='auto', norm=norm, interpolation='nearest')

    plt.colorbar(label='score')

    step = 5
    ticks = np.arange(0, len(scoreboard), step)
    plt.xticks(ticks, ticks)

    plt.xlabel("marks")

    plt.show()

def displayBoards(truth, reversedTruth, scoreboard):
    boards = np.vstack([truth, reversedTruth, scoreboard])

    plt.figure(figsize=(20, 3))

    norm = colors.TwoSlopeNorm(
        vmin = np.min(boards),
        vcenter = 0.0,
        vmax = np.max(boards)
    )

    plt.imshow(boards, cmap='bwr', aspect='auto', norm=norm, interpolation='nearest')

    plt.colorbar(label='score')

    plt.yticks([0, 1, 2], ['Sol', 'Reversed Sol', 'Rand Partial Sols'])

    step = 5
    ticks = np.arange(0, len(truth), step)
    plt.xticks(ticks, ticks)

    plt.xlabel("marks")

    plt.show()


def golombTesting():
    F, baseCutoff = encodeRuler()
    
    baseClauses = F.clauses[:baseCutoff]
    constraintClauses = F.clauses[baseCutoff:]
    print(f"base clauses: {len(baseClauses)}, constraint clauses: {len(constraintClauses)}")

    numIterations = 30
    pctRandom = 96

    # solution, normalTime = golombSAT(F, False)
    # print("finished normal solve.")

    # solutionBoard = [r * 10.0 for r in rulerToBoard(solution)]
    # reversedSolutionBoard = [0.0] * (UPPER_L + 1)
    # for i in range(len(solutionBoard)):
    #     if solutionBoard[i] > 0:
    #         reversedSolutionBoard[UPPER_L - i] = 10.0

    scoreboard = [0.0] * (UPPER_L + 1)
    scoreboardTime = time.perf_counter()
    for i in range(numIterations):
        randF = CNF()
        random.shuffle(baseClauses)
        randF.extend(baseClauses)

        # select random subset of constraint clauses
        sampled = random.sample(constraintClauses, int(len(constraintClauses) * pctRandom / 100))
        randF.extend(sampled)

        r, _ = golombSAT(randF, False)
        r = rulerToBoard(r)
        scoreboard = updateBoard(scoreboard, r)
        print(f"iteration {i + 1}/{numIterations} complete.")

    scoreboardTime = time.perf_counter() - scoreboardTime

    # print(f"Normal SAT time: {normalTime} seconds")
    print(f"Scoreboard time: {scoreboardTime} seconds")
    # print("Solution Board:", solutionBoard)
    displayBoard(scoreboard)
    # displayBoards(solutionBoard, reversedSolutionBoard, scoreboard)

    return scoreboard