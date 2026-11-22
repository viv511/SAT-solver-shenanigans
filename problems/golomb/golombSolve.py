"""
golombSolve.py

Same structure as crossing.py: baseline and heuristic solves both use the
modified MiniSat binary (empty scorecard ==> plain MiniSat).

Each solve is repeated over SEEDS (MiniSat's -rnd-seed) and we compare the
median conflicts, since a single run is way too noisy to compare.

All times are MiniSat's own reported CPU time (parse + simplify + solve), for
the baseline, every relaxed sample, and the heuristic solve alike, so Python
and file/process overhead is excluded equally from both arms.

Run from this folder: python3 golombSolve.py
"""

import random
import subprocess
import statistics

from pysat.formula import CNF

from encoding2 import encodingTwo, getRulerTwo
from golomb import verifyRuler

DEBUG = False  # progress bar + "Generation done!" for each scorecard

# CONSTANTS
ORDER = 12
LENGTH = 85

# For scorecard generation
# with TRUE_WEIGHT = 1, FALSE_WEIGHT = 0: score = # of samples that marked the position,
# so THRESHOLD = 9.5 means "forced if marked in >= 10 of the 20 samples"
THRESHOLD = 4.5
NUM_ITERATIONS = 10
PCT_RAND = 95
TRUE_WEIGHT = 1
FALSE_WEIGHT = 0

SEEDS = range(1, 21)

# More positive the board, the more likely it is to be true (vice versa!)
def updateBoard(inputBoard, updateBoard):
    for i in range(len(inputBoard)):
        if updateBoard[i] > 0:
            inputBoard[i] += TRUE_WEIGHT
        else:
            inputBoard[i] -= FALSE_WEIGHT
    return inputBoard

# returns the model, MiniSat's CPU time, and its conflict count
def solveModified(cnf, cnfFile, seed=1):
    with open(cnfFile, "w") as f:
        cnf.to_fp(f)

    result = solveLocalModified(cnfFile, seed)
    model = modelFromResult("result.out")
    stats = result.stdout.splitlines()
    conflicts = [int(l.split()[2]) for l in stats if l.startswith("conflicts")][0]
    cpuTime = [float(l.split()[3]) for l in stats if l.startswith("CPU time")][0]

    return model, cpuTime, conflicts

def solveLocalModified(cnfFile, seed):
    return subprocess.run(
        ["../../solvers/modifiedMinisat/build/release/bin/minisat",
        "-rnd-freq=0.01", f"-rnd-seed={seed}", cnfFile, "result.out"],
        capture_output=True,
        text=True
    )

def modelFromResult(resultFile):
    with open(resultFile, "r") as f:
        lines = f.readlines()

    if lines[0].strip() != "SAT":
        raise Exception("UNSAT")

    model = []
    for lit in lines[1].split():
        val = int(lit)
        if val != 0:
            model.append(val)

    return model

# x(i) = i + 1, so the base variables are 1..LENGTH+1
def rulerToBoard(ruler):
    return [1 if i in ruler else -1 for i in range(LENGTH + 1)]

def generateScorecard(length, baseClauses, additionalClauses):
    progressBarLen = 30  # just because i like looking at nice looking progress bars
    scorecard = [0.0] * length
    generationTime = 0.0  # sum of MiniSat CPU time over all relaxed solves

    for i in range(NUM_ITERATIONS):
        randF = CNF()
        randF.extend(baseClauses)

        # select random subset of constraint clauses
        sampled = random.sample(additionalClauses, int(len(additionalClauses) * PCT_RAND / 100))
        randF.extend(sampled)

        model, cpuTime, _ = solveModified(randF, "Fsubset.cnf")
        generationTime += cpuTime

        assignmentFromSubset = rulerToBoard(getRulerTwo(model, ORDER, LENGTH))

        # takes a alpha assignment for the partial CNF and updates scorecard via the weights
        scorecard = updateBoard(scorecard, assignmentFromSubset)

        # nice looking progress bar because why not
        if DEBUG:
            done = int((i + 1) / NUM_ITERATIONS * progressBarLen)
            bar = "#" * done + "-" * (progressBarLen - done)
            print(f"\r[{bar}]", end="", flush=True)

    if DEBUG:
        print(" Generation done!\n")

    return scorecard, generationTime

def writeScorecard(path, threshold, variables, scores):
    with open(path, "w") as f:
        f.write(f"{threshold}\n")
        for var, score in zip(variables, scores):
            f.write(f"{var} {score}\n")

# solves F once per seed, checks every ruler, returns median conflicts + median CPU time
def solveSeeds(F, label):
    conflictsList, times = [], []

    for seed in SEEDS:
        model, t, conflicts = solveModified(F, "golomb.cnf", seed)
        ruler = getRulerTwo(model, ORDER, LENGTH)

        if not verifyRuler(ruler, ORDER):
            raise Exception(f"invalid ruler ({label}, seed {seed}): {ruler}")

        conflictsList.append(conflicts)
        times.append(t)

    print(f"{label:<10} median conflicts {statistics.median(conflictsList):>9.0f}   "
            f"median cpu {statistics.median(times):.3f}s   all conflicts: {sorted(conflictsList)}")

    return statistics.median(conflictsList), statistics.median(times)


print(f"ORDER = {ORDER}, LENGTH = {LENGTH}")
print(f"THRESHOLD = {THRESHOLD}, NUM_ITERATIONS = {NUM_ITERATIONS}, PCT_RAND = {PCT_RAND}, "
    f"TRUE_WEIGHT = {TRUE_WEIGHT}, FALSE_WEIGHT = {FALSE_WEIGHT}")
print(f"SEEDS = {list(SEEDS)}\n")

F, base = encodingTwo(ORDER, LENGTH)
print(f"total clauses: {len(F.clauses)}")
print(f"└──> base clauses: {base}, additional clauses: {len(F.clauses) - base}\n")

# BASELINE SOLVE (empty scorecard ==> plain minisat)
writeScorecard("scorecard.txt", 0, [], [])
normalConflicts, normalSolveTime = solveSeeds(F, "baseline")
print()

# HEURISTIC: one full pipeline per seed (new scorecard + solve), so every run pays its own generation cost
totals, genTimes, solveTimes, conflictsList = [], [], [], []

for seed in SEEDS:
    random.seed(seed)
    scorecard, genTime = generateScorecard(LENGTH + 1, F.clauses[:base], F.clauses[base:])
    writeScorecard("scorecard.txt", THRESHOLD, range(1, LENGTH + 2), scorecard)

    model, t, conflicts = solveModified(F, "golomb.cnf", seed)
    ruler = getRulerTwo(model, ORDER, LENGTH)

    if not verifyRuler(ruler, ORDER):
        raise Exception(f"invalid ruler (heuristic, seed {seed}): {ruler}")

    totals.append(genTime + t)
    genTimes.append(genTime)
    solveTimes.append(t)
    conflictsList.append(conflicts)

    if DEBUG:
        print(f"seed {seed:<3} forced marks: {[i for i, s in enumerate(scorecard) if abs(s) > THRESHOLD]}   "
              f"conflicts {conflicts}   cpu {genTime:.3f} + {t:.3f} = {genTime + t:.3f}s")

print(f"\nCONFLICTS (median):\t\t\t {normalConflicts:.0f} (baseline) vs {statistics.median(conflictsList):.0f} (heuristic)")
print("NORMAL SOLVE CPU (median):\t\t", normalSolveTime)
print("HEURISTIC TOTAL CPU (median):\t\t", statistics.median(totals))
print("└──> median generation + median solve:\t", statistics.median(genTimes), "+", statistics.median(solveTimes), "\n")
