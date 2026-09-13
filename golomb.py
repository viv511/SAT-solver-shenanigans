from matplotlib import colors
from pysat.formula import CNF
from pysat.card import *
from pysat.solvers import Minisat22
import numpy as np
import matplotlib.pyplot as plt
import time, random

from encoding1 import *
from encoding2 import *

'''
todo:

Your current setup is actually ideal for this: treat LENGTH as a maximum coordinate/buffer, build the CNF once for positions 0..LENGTH, and use SAT assumptions to test smaller candidate lengths without rebuilding anything. If x(i) means “position i is a mark,” then asking whether a ruler has length <= B is equivalent to temporarily assuming x(B+1), ..., x(LENGTH) are all false. In PySAT that is simply solver.solve(assumptions=[-x(i) for i in range(B + 1, LENGTH + 1)]). The assumptions are temporary, so the next solve can use a different bound, and—crucially—the solver keeps its learned clauses from previous solves. Since satisfiability is monotonic (if a ruler of length B exists, then one of length B+1 also exists), you can binary-search the optimum: for ORDER=11, the basic lower bound is 11*10//2 = 55, so with MAX_LENGTH=75 you start with lo=55, hi=75; test mid=65, and if UNSAT set lo=66, otherwise set hi=65; continue until lo == hi, which is the optimal length. In code, the core is: def assumptions_for_bound(bound, max_length): return [-x(i) for i in range(bound + 1, max_length + 1)] and def find_optimal_length(solver, order, max_length): lo = order * (order - 1) // 2; hi = max_length; while lo < hi: mid = (lo + hi) // 2; if solver.solve(assumptions=assumptions_for_bound(mid, max_length)): hi = mid; else: lo = mid + 1; return lo. Then build your encoding once with cnf = encodingTwo(ORDER, MAX_LENGTH), create one solver, call optimal = find_optimal_length(solver, ORDER, MAX_LENGTH), and finally call solver.solve(assumptions=assumptions_for_bound(optimal, MAX_LENGTH)) and extract the model with getRuler; because the previous bound optimal-1 was proven UNSAT, the returned ruler must actually have final mark exactly optimal. The important distinction is that you should not permanently add -x(i) clauses between searches; use assumptions= so every candidate bound is temporary while MiniSat retains its learned information.
'''

# if u update, make sure you update modifiedMinisat/minisat/core/Solver.h lines 39-40
ORDER = 11
LENGTH = 75

def encodeRuler():
    # return encodingOne(ORDER, LENGTH)
    return encodingTwo(ORDER, LENGTH)

def getRuler(model):
    # return getRulerOne(model, ORDER, LENGTH)
    return getRulerTwo(model, ORDER, LENGTH)

def verifyRuler(ruler, ORDER=ORDER):
    dists = set()

    if len(ruler) != ORDER:
        return False

    for i in range(len(ruler)):
        for j in range(i + 1, len(ruler)):
            d = abs(ruler[i] - ruler[j])
            if d in dists:
                # print("Duplicate distance:", d)
                return False
            dists.add(d)

    
    return True

def reverseRuler(ruler):
    return sorted([LENGTH - r for r in ruler])

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
        return getRuler(model), end - start
    else:
        if prettyPrint:
            print("UNSAT")
    raise Exception("shouldn't be here")

def rulerToBoard(ruler):
    b = [0.0] * (LENGTH + 1)
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