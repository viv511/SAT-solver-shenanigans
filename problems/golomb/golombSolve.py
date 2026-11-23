import random
import subprocess
import statistics

from pysat.formula import CNF

from encoding2 import encodingTwo, getRulerTwo
from golomb import verifyRuler

DEBUG = True

# CONSTANTS
ORDER = 13
LENGTH = 120

# For scorecard generation (same constants as the old "faulty" 12/93 run)
TOP_PCT = 10 # force the top TOP_PCT% of positions 1..LENGTH-1 by |score|; None ==> use THRESHOLD
THRESHOLD = 4.5 # score = # samples marking the position, so forced if marked in >= 5 of 10
NUM_ITERATIONS = 10
PCT_RAND = 95
TRUE_WEIGHT = 1
FALSE_WEIGHT = 0

SEEDS = range(1, 11) # in the heuristic loop, each seed is one round

# TRANSFER TEST: build ONE scorecard from real rulers of an easy instance, reuse it on every target + seed
TRANSFER = False
SOURCE_LENGTH = 110
SOURCE_SOLVES = 20
TARGET_LENGTHS = [96, 95, 94]
TRANSFER_TOP_PCT = 10
TRANSFER_SEEDS = range(32, 52) # fresh: seeds 1-31 were used to pick + confirm this config on 12/96

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

# NO scorecard reset: the samples are solved with the previous round's scorecard still active (iterative)
def generateScorecard(length, baseClauses, additionalClauses):
    progressBarLen = 30
    scorecard = [0.0] * length
    generationTime = 0.0  # sum of MiniSat CPU time over all relaxed solves

    # no reset, add it back later if u want

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

# top TOP_PCT% of positions 1..LENGTH-1 by |score| (0 and LENGTH are fixed by the encoding), ties -> lower position
def topPositions(scorecard):
    ranked = sorted(range(1, LENGTH), key=lambda i: -abs(scorecard[i]))
    m = max(1, round(TOP_PCT / 100 * (LENGTH - 1)))
    return [i for i in ranked[:m] if scorecard[i] != 0]

# greedy top TRANSFER_TOP_PCT% of positions 1..length-1 by score, skipping any position that would
# repeat a distance with the marks already chosen (incl. 0) ==> the forced marks are a valid partial ruler
def consistentTop(scores, length):
    m = max(1, round(TRANSFER_TOP_PCT / 100 * (length - 1)))
    chosen, dists = [0], set()

    for i in sorted(range(1, length), key=lambda i: -scores[i]):
        if len(chosen) - 1 == m or scores[i] == 0:
            break
        new = [abs(i - j) for j in chosen]
        if len(set(new)) == len(new) and not dists.intersection(new):
            chosen.append(i)
            dists.update(new)

    return chosen[1:]

def transferTest():
    # 1. BUILD ONCE: real rulers from the easy source instance (full formula, empty scorecard)
    S, _ = encodingTwo(ORDER, SOURCE_LENGTH)
    writeScorecard("scorecard.txt", 0, [], [])
    rulers, buildTime = [], 0.0

    for seed in range(1001, 1001 + SOURCE_SOLVES):
        model, t, _ = solveModified(S, "source.cnf", seed)
        rulers.append(getRulerTwo(model, ORDER, SOURCE_LENGTH))
        buildTime += t

    print(f"scorecard built from {SOURCE_SOLVES} rulers of {ORDER}/{SOURCE_LENGTH}: {buildTime:.3f}s CPU, paid ONCE for every target and seed\n")

    allBase, allTransfer = 0.0, 0.0

    for L in TARGET_LENGTHS:
        # 2. MAP: stretch each source ruler onto length L, count how often each position gets a mark
        scores = [0] * (L + 1)
        for r in rulers:
            for i in r:
                scores[round(i * L / r[-1])] += 1

        forced = consistentTop(scores, L)
        shuffled = random.Random(0).sample(range(1, L), len(forced)) # control: same # of forced marks, random positions
        F, _ = encodingTwo(ORDER, L)
        times = {}

        # 3. SOLVE: same seeds for all three arms
        for label, positions in [("baseline", []), ("transfer", forced), ("shuffled", shuffled)]:
            writeScorecard("scorecard.txt", 0, [i + 1 for i in positions], [scores[i] for i in forced])
            times[label], conflictsList = [], []

            for seed in TRANSFER_SEEDS:
                model, t, conflicts = solveModified(F, "golomb.cnf", seed)
                ruler = getRulerTwo(model, ORDER, L)

                if not verifyRuler(ruler, ORDER):
                    raise Exception(f"invalid ruler ({ORDER}/{L} {label}, seed {seed}): {ruler}")

                times[label].append(t)
                conflictsList.append(conflicts)

                if DEBUG:
                    print(f"  {ORDER}/{L} {label} seed {seed}: {conflicts} conflicts, {t:.3f}s")

            print(f"{ORDER}/{L} {label:<9} median cpu {statistics.median(times[label]):7.3f}s   max {max(times[label]):7.3f}s   "
                  f"median conflicts {statistics.median(conflictsList):>9.0f}")

        wins = sum(t < b for t, b in zip(times["transfer"], times["baseline"]))
        print(f"└──> forced marks {sorted(forced)}, transfer faster than baseline on {wins}/{len(TRANSFER_SEEDS)} seeds\n")

        allBase += sum(times["baseline"])
        allTransfer += sum(times["transfer"])

    print(f"TOTAL CPU over all targets + seeds: baseline {allBase:.1f}s vs transfer {buildTime:.1f}s (build once) + {allTransfer:.1f}s = {buildTime + allTransfer:.1f}s")

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


if TRANSFER:
    print(f"TRANSFER: ORDER = {ORDER}, SOURCE = {ORDER}/{SOURCE_LENGTH} x {SOURCE_SOLVES} solves, TARGETS = {TARGET_LENGTHS}, "
          f"TRANSFER_TOP_PCT = {TRANSFER_TOP_PCT}, SEEDS = {list(TRANSFER_SEEDS)}\n")
    transferTest()
    exit()

print(f"ORDER = {ORDER}, LENGTH = {LENGTH}")
print(f"TOP_PCT = {TOP_PCT}, THRESHOLD = {THRESHOLD}, NUM_ITERATIONS = {NUM_ITERATIONS}, PCT_RAND = {PCT_RAND}, "
    f"TRUE_WEIGHT = {TRUE_WEIGHT}, FALSE_WEIGHT = {FALSE_WEIGHT}")
print(f"SEEDS = {list(SEEDS)}\n")

F, base = encodingTwo(ORDER, LENGTH)
print(f"total clauses: {len(F.clauses)}")
print(f"└──> base clauses: {base}, additional clauses: {len(F.clauses) - base}\n")

# BASELINE SOLVE (empty scorecard ==> plain minisat)
writeScorecard("scorecard.txt", 0, [], [])
normalConflicts, normalSolveTime = solveSeeds(F, "baseline")
print()

# HEURISTIC (iterative): round 1 samples use the empty baseline scorecard, round r samples use round r-1's scorecard.
# The cost of round r is CUMULATIVE: all generation from rounds 1..r + round r's final solve
totals, genTimes, solveTimes, conflictsList = [], [], [], []
cumulativeGen = 0.0

for seed in SEEDS:
    random.seed(seed)
    scorecard, genTime = generateScorecard(LENGTH + 1, F.clauses[:base], F.clauses[base:])
    cumulativeGen += genTime
    # only the chosen positions go in the scorecard, threshold 0 ==> solver forces all of them, highest |score| first
    forced = topPositions(scorecard) if TOP_PCT else [i for i, s in enumerate(scorecard) if abs(s) > THRESHOLD]
    writeScorecard("scorecard.txt", 0, [i + 1 for i in forced], [scorecard[i] for i in forced])

    model, t, conflicts = solveModified(F, "golomb.cnf", seed)
    ruler = getRulerTwo(model, ORDER, LENGTH)

    if not verifyRuler(ruler, ORDER):
        raise Exception(f"invalid ruler (heuristic, seed {seed}): {ruler}")

    totals.append(cumulativeGen + t)
    genTimes.append(genTime)
    solveTimes.append(t)
    conflictsList.append(conflicts)

    if DEBUG:
        print(f"round {seed:<3} true: {[i for i in forced if scorecard[i] > 0]}   false: {[i for i in forced if scorecard[i] < 0]}   "
              f"conflicts {conflicts}   cpu: this round gen {genTime:.3f}, cumulative gen {cumulativeGen:.3f} + solve {t:.3f} = {cumulativeGen + t:.3f}s")

# rounds are chained (not independent), so the per-round lines above are the real result; medians are just a summary
print(f"\nCONFLICTS (median over rounds):\t\t {normalConflicts:.0f} (baseline) vs {statistics.median(conflictsList):.0f} (heuristic)")
print(f"LAST ROUND:\t\t\t\t {conflictsList[-1]} conflicts, cumulative cpu {totals[-1]:.3f}s")
print("NORMAL SOLVE CPU (median):\t\t", normalSolveTime)
print("HEURISTIC CUMULATIVE CPU (median):\t", statistics.median(totals))
print("└──> median round generation + median solve:\t", statistics.median(genTimes), "+", statistics.median(solveTimes), "\n")
