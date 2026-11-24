"""
golombSolve.py

Find a Golomb ruler with ORDER marks and length <= TARGET_LENGTH using a scorecard
built from an EASIER instance (same order, length SOURCE_LENGTH):

    1. BUILD: solve the easy SOURCE instance NUM_SAMPLES times (PCT_RAND = 100 ==> real rulers),
       stretch each ruler onto the target length, score every position, save to SCORECARD_FILE
    2. SOLVE: the TARGET once with plain MiniSat and once with the saved scorecard

Run from this folder: python3 golombSolve.py
"""

import os
import random
import shutil
import subprocess

from pysat.formula import CNF

from encoding2 import encodingTwo, getRulerTwo
from golomb import verifyRuler

# CONSTANTS
ORDER = 12
SOURCE_LENGTH = 96
TARGET_LENGTH = 96

BUILD_SCORECARD = True # False ==> skip building, reuse the SCORECARD_FILE saved by an earlier run
SCORECARD_FILE = f"scorecard_{ORDER}_{SOURCE_LENGTH}_to_{TARGET_LENGTH}.txt"

NUM_SAMPLES = 10
PCT_RAND = 95
TRUE_WEIGHT = 85   # = LENGTH + 1 - ORDER
FALSE_WEIGHT = 12  # = ORDER
TOP_PCT = None     # threshold mode, so FALSE marks can be forced too
THRESHOLD = 100
CPU_LIMIT = 600
SEED = 1 # MiniSat seed for the two target solves; change between runs to check the scorecard isn't a lucky seed

# More positive the board, the more likely it is to be true (vice versa!)
def updateBoard(inputBoard, updateBoard):
    for i in range(len(inputBoard)):
        if updateBoard[i] > 0:
            inputBoard[i] += TRUE_WEIGHT
        else:
            inputBoard[i] -= FALSE_WEIGHT
    return inputBoard

# returns the model (None if it hit CPU_LIMIT), MiniSat's CPU time, and its conflict count
def solveModified(cnf, cnfFile, seed=1):
    with open(cnfFile, "w") as f:
        cnf.to_fp(f)

    if os.path.exists("result.out"):
        os.remove("result.out") # MiniSat doesn't write it on a timeout, so don't read a stale one

    result = solveLocalModified(cnfFile, seed)
    stats = result.stdout.splitlines()
    conflicts = [int(l.split()[2]) for l in stats if l.startswith("conflicts")][0]
    cpuTime = [float(l.split()[3]) for l in stats if l.startswith("CPU time")][0]

    # CPU_LIMIT hit: during search MiniSat prints INDETERMINATE, during parsing/simplification INTERRUPTED
    if "INDETERMINATE" in result.stdout or "INTERRUPTED" in result.stdout:
        return None, cpuTime, conflicts

    return modelFromResult("result.out"), cpuTime, conflicts

def solveLocalModified(cnfFile, seed):
    return subprocess.run(
        ["../../solvers/modifiedMinisat/build/release/bin/minisat",
        "-rnd-freq=0.01", f"-rnd-seed={seed}", f"-cpu-lim={CPU_LIMIT}", cnfFile, "result.out"],
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

# stretch a source ruler onto the target length: mark i of a ruler of length r[-1] goes to i * TARGET_LENGTH / r[-1]
# SOURCE_LENGTH == TARGET_LENGTH ==> relaxed samples of the same instance, so no stretching
def stretchToBoard(ruler):
    scale = 1 if SOURCE_LENGTH == TARGET_LENGTH else TARGET_LENGTH / ruler[-1]
    stretched = {round(i * scale) for i in ruler}
    return [1 if i in stretched else -1 for i in range(TARGET_LENGTH + 1)]

def generateScorecard():
    S, base = encodingTwo(ORDER, SOURCE_LENGTH)
    writeScorecard("scorecard.txt", 0, [], []) # source is solved with plain MiniSat
    scorecard = [0.0] * (TARGET_LENGTH + 1)
    generationTime = 0.0
    progressBarLen = 40

    for i in range(NUM_SAMPLES):
        randF = CNF()
        randF.extend(S.clauses[:base])
        randF.extend(random.sample(S.clauses[base:], int(len(S.clauses[base:]) * PCT_RAND / 100)))

        # sample i uses MiniSat seed i, otherwise full-formula samples would all return the same ruler
        model, cpuTime, _ = solveModified(randF, "source.cnf", i + 1)
        generationTime += cpuTime

        if model is not None:
            ruler = getRulerTwo(model, ORDER, SOURCE_LENGTH)
            if ruler[1] > ruler[-1] - ruler[-2]: # symmetry break
                ruler = sorted(ruler[-1] - i for i in ruler)

            scorecard = updateBoard(scorecard, stretchToBoard(ruler))

        # nice looking progress bar because why not
        done = int((i + 1) / NUM_SAMPLES * progressBarLen)
        print(f"\r[{'#' * done}{'-' * (progressBarLen - done)}]", end="", flush=True)

    print(" Generation done!\n")
    return scorecard, generationTime

# positions to force, best first: TRUE marks (score > THRESHOLD, or the top TOP_PCT%) that never repeat a
# distance with each other or with 0, plus FALSE marks (score < -THRESHOLD) when FALSE_WEIGHT > 0
def chooseForced(scorecard):
    m = round(TOP_PCT / 100 * (TARGET_LENGTH - 1)) if TOP_PCT else TARGET_LENGTH
    chosen, dists = [0], set()

    for i in sorted(range(1, TARGET_LENGTH), key=lambda i: -scorecard[i]):
        if len(chosen) - 1 == m or scorecard[i] <= (0 if TOP_PCT else THRESHOLD):
            break
        new = [abs(i - j) for j in chosen]
        if len(set(new)) == len(new) and not dists.intersection(new):
            chosen.append(i)
            dists.update(new)

    forcedFalse = [] if TOP_PCT else [i for i in range(1, TARGET_LENGTH) if scorecard[i] < -THRESHOLD]
    return chosen[1:], forcedFalse

def writeScorecard(path, threshold, variables, scores):
    with open(path, "w") as f:
        f.write(f"{threshold}\n")
        for var, score in zip(variables, scores):
            f.write(f"{var} {score}\n")

def report(label, model, cpuTime, conflicts):
    if model is None:
        print(f"{label:<10} TIMEOUT after {cpuTime:.3f}s CPU ({conflicts} conflicts)")
        return

    ruler = getRulerTwo(model, ORDER, TARGET_LENGTH)
    if not verifyRuler(ruler, ORDER):
        raise Exception(f"invalid ruler ({label}): {ruler}")

    print(f"{label:<10} {cpuTime:9.3f}s CPU   {conflicts:>10} conflicts   ruler (length {ruler[-1]}): {ruler}")


print(f"ORDER = {ORDER}, SOURCE_LENGTH = {SOURCE_LENGTH}, TARGET_LENGTH = {TARGET_LENGTH}")
print(f"NUM_SAMPLES = {NUM_SAMPLES}, PCT_RAND = {PCT_RAND}, TRUE_WEIGHT = {TRUE_WEIGHT}, FALSE_WEIGHT = {FALSE_WEIGHT}, "
      f"TOP_PCT = {TOP_PCT}, THRESHOLD = {THRESHOLD}, CPU_LIMIT = {CPU_LIMIT}, SEED = {SEED}\n")

# 1. BUILD the scorecard from the easy SOURCE instance and save it
# only the forced positions are written, threshold 0 ==> the solver forces all of them, highest |score| first
if BUILD_SCORECARD:
    scorecard, generationTime = generateScorecard()
    forcedTrue, forcedFalse = chooseForced(scorecard)
    forced = forcedTrue + forcedFalse
    writeScorecard(SCORECARD_FILE, 0, [i + 1 for i in forced], [scorecard[i] for i in forced])
    print(f"scorecard built in {generationTime:.3f}s CPU from {NUM_SAMPLES} solves of {ORDER}/{SOURCE_LENGTH}, saved to {SCORECARD_FILE}")
    print(f"└──> forced TRUE {sorted(forcedTrue)}, forced FALSE {sorted(forcedFalse)}\n")

# 2. SOLVE the TARGET once without and once with the scorecard
F, _ = encodingTwo(ORDER, TARGET_LENGTH)

writeScorecard("scorecard.txt", 0, [], []) # empty ==> plain MiniSat
report("baseline", *solveModified(F, "golomb.cnf", SEED))

shutil.copy(SCORECARD_FILE, "scorecard.txt") # the solver always reads scorecard.txt
report("heuristic", *solveModified(F, "golomb.cnf", SEED))
