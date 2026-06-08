from costas import *
from golomb import *
import subprocess
import time
import os

# CONFIGURABLE PARAMATERS!!
numIterations = 10
pctRandom = 97
trueWeightage = 5
falseWeightage = 1

# More positive the board, the more likely it is to be true (vice versa!)
def updateBoard(inputBoard, updateBoard):
    for i in range(len(inputBoard)):
        if updateBoard[i] > 0:
            inputBoard[i] += trueWeightage
        else:
            inputBoard[i] -= falseWeightage
    return inputBoard

'''
length = cardinality of "base variables"
baseClauses = clauses that only involve base variables (the "core" of the problem)
    > think of this as the "basic rules"
additionalClauses = the majority of the clauses, the constraints that make the problem hard
    > think of this as the "conditions"
'''
def generateScorecard(length, baseClauses, additionalClauses):
    progressBarLen = 50 #just because i like looking at nice looking progress bars
    scorecard = [0.0] * length

    start = time.perf_counter()

    for i in range(numIterations):
        randF = CNF()
        randF.extend(baseClauses)

        # Select random subset of constraint clauses
        sampled = random.sample(additionalClauses, int(len(additionalClauses) * pctRandom / 100))
        randF.extend(sampled)

        r, _ = golombSAT(randF, False)
        assignmentFromSubset = rulerToBoard(r)

        # Takes a alpha assignment for the partial CNF and updates scorecard via the weights
        scorecard = updateBoard(scorecard, assignmentFromSubset)

        # nice looking progress bar because why not
        done = int((i + 1) / numIterations * progressBarLen)
        bar = "#" * done + "-" * (progressBarLen - done)
        print(f"\r[{bar}] {i+1}/{numIterations}", end="", flush=True)

    end = time.perf_counter()

    generationTime = end - start

    print(" Generation done!\n")

    return scorecard, generationTime

def solveLocalModified(cnfFile):
    start = time.perf_counter()
    result = subprocess.run(
            ["./modifiedMinisat/build/release/bin/minisat", cnfFile, "result.out"],
            capture_output=False,
            text=True
        )
    end = time.perf_counter()

    return result, end - start

def modelFromRuler(resultFile):
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

# somehow `make`` the `modifiedMinisat` folder?

# Encode Golomb Ruler
print("Golomb Ruler of order", ORDER, "and length", LENGTH)

F, baseCutoff = encodeRuler()

print(f"\ntotal clauses: {len(F.clauses)}")
print(f"└──> base clauses: {baseCutoff}, additional clauses: {len(F.clauses) - baseCutoff}\n")

# Write CNF to file for modified MiniSAT
with open("golomb.cnf", "w") as f:
    F.to_fp(f)

# NORMAL MINISAT SOLVE
solver = Minisat22()
solver.append_formula(F.clauses)

start = time.perf_counter()
res = solver.solve()
end = time.perf_counter()

normalSolveTime = end - start

if res:
    ruler = getRuler(solver.get_model())
    print("Ruler:\t", ruler)
    print("Valid?", verifyRuler(ruler))

else:
    print("UNSAT... issue with encoding?")
    exit(1)

print(f"Time to solve: {normalSolveTime} seconds")

exit(1)


# GENERATING HEURISTIC SCORECARD
print(f"\nbase clauses: {baseCutoff}, additional clauses: {len(F.clauses) - baseCutoff}\n")
scorecard, heuristicTime = generateScorecard(LENGTH + 1, F.clauses[:baseCutoff], F.clauses[baseCutoff:]) 
print(scorecard)

# MODIFIED MINISAT SOLVE
_, heuristicSolveTime = solveLocalModified("golomb.cnf")
ruler = getRuler(modelFromRuler("result.out"))

print("Ruler:\t", ruler)
# print("Valid?", verifyRuler(ruler))

print("\nNORMAL SOLVE TIME:\t\t\t", normalSolveTime)
print("HEURISTIC SOLVE TIME:\t\t\t", heuristicSolveTime + heuristicTime)
print("└──> SPLIT:\t\t\t\t", heuristicTime, "+", heuristicSolveTime, "\n")

'''
CREDITS:
- John Mackey, Marijn Heule, & Bernardo Subercaseaux for the inspiration (and future support!?)
- Vipin Bhat for the guidance + initial Costas Arrays YEET Session
- my roommate (Rushil Surti!) for listening to me yap about this lol
- https://ieeexplore.ieee.org/document/8261784
- shotgun sequencing w/ dna ig cause the human genome sequencing project is where i got the idea from








TODO: 
Reduce clause count by introducing auxiliary vars for each difference-triangle entry.
For each displacement k and start column i, create Boolean variables D[k,i,v] meaning:
“p(i+k) - p(i) = v”, where v ∈ {-(n-1), …, -1, 1, …, (n-1)}.

Then link these to your existing one-hot x(i,j) by implication clauses:
- for every valid a with a+v in-bounds, add (x(i,a) ∧ x(i+k,a+v)) → D[k,i,v),
- i.e. [-x(i,a), -x(i+k,a+v), D[k,i,v]].

Optionally also add the reverse direction D[k,i,v] → OR_a (x(i,a) ∧ x(i+k,a+v))
(usually encoded as multiple clauses or omitted if you instead enforce “exactly one v per (k,i)”).

Next, enforce exactly one difference value per triangle cell:
for fixed (k,i), exactlyOne({D[k,i,v]}).

Finally, enforce row-wise all-different: for fixed k and difference v,
you cannot have two positions i1≠i2 both taking v, so add pairwise clauses [-D[k,i1,v], -D[k,i2,v]].
That last step is what replaces the 4-literal “forbid equal differences” clauses and yields the O(n⁴) scaling.
'''

'''
def costasProperty():
    clauses = []
    n = COSTAS_ARRAY_SIZE
    
    # 1. Define the witness variable mapping
    # Offset starts after the n^2 grid variables
    def d(k, i, z):
        z_idx = z + (n - 1) # Shift z to be 0 to 2n-2
        return (n * n + 1) + (k * n * 2 * n) + (i * 2 * n) + z_idx

    # 2. THE LINKING (O(n^4))
    # This turns on the 'witness' if two dots create a specific shift z
    for k in range(1, n):
        for i in range(n - k):
            for h1 in range(n):      # Height at column i
                for h2 in range(n):  # Height at column i+k
                    if h1 == h2: continue
                    z = h2 - h1
                    
                    # Logic: (x[i, h1] AND x[i+k, h2]) -> d[k, i, z]
                    # CNF: (-x1 OR -x2 OR d)
                    clauses.append([-x(i, h1, n), -x(i + k, h2, n), d(k, i, z)])

    # 3. THE COSTAS PROPERTY (O(n^3))
    # In row 'k' of the triangle, each shift 'z' happens AT MOST ONCE
    for k in range(1, n):
        for z in range(-(n - 1), n):
            if z == 0: continue
            
            # Collect all witnesses for this specific vertical shift in this row
            witnesses = [d(k, i, z) for i in range(n - k)]
            
            if len(witnesses) > 1:
                # AMO constraint: ensures only one witness can be TRUE
                # CardEnc.atmost is O(N) or O(N log N), making this O(n^3) total
                amo = CardEnc.atmost(witnesses, bound=1, encoding=EncType.pairwise)
                clauses.extend(amo.clauses)

    return clauses
'''


