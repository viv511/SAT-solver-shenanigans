from matplotlib import colors
from pysat.formula import CNF
from pysat.card import *
from pysat.solvers import Minisat22
import numpy as np
import matplotlib.pyplot as plt
import time, random

from encoding1 import *
from encoding2 import *

# if u update, make sure you update modifiedMinisat/minisat/core/Solver.h lines 39-40
ORDER = 12
LENGTH = 87

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