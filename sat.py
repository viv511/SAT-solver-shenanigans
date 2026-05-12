from costas import *
from golomb import *
import subprocess

# CONFIGURABLE PARAMATERS!!
numIterations = 30
pctRandom = 96

def solveLocal(F, cnfFile):
    with open("golomb.cnf", "w") as f:
        F.to_fp(f)

    start = time.perf_counter()
    result = subprocess.run(
            ["./minisat/build/release/bin/minisat", cnfFile, "result.out"],
            capture_output=True,
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

# Encode Golomb Ruler
F, baseCutoff = encodeRuler()

# Write PySAT CNF to file to run modified MiniSAT on it
result, timeToSolve = solveLocal(F, "golomb.cnf")
print(f"\nNormal solve time: {timeToSolve} seconds\n")

# print(result.stdout)
# this is the actual stats, dont care about it right now exactly

ruler = displayRuler(modelFromRuler("result.out"))
print("Ruler:", ruler)
print("Valid?", verifyRuler(ruler))
print("\n")

# Separate clauses
baseClauses = F.clauses[:baseCutoff]
constraintClauses = F.clauses[baseCutoff:]
print(f"base clauses: {len(baseClauses)}, constraint clauses: {len(constraintClauses)}")

# Make clean scorecard
scoreboard = [0.0] * (UPPER_L + 1)

scoreboardTime = time.perf_counter()

for i in range(numIterations):
    randF = CNF()
    random.shuffle(baseClauses)
    randF.extend(baseClauses)

    # Select random subset of constraint clauses
    sampled = random.sample(constraintClauses, int(len(constraintClauses) * pctRandom / 100))
    randF.extend(sampled)

    # NOTE: Although the end result is using a modified MiniSAT, to build the initial heuristic,
    # im using the out of the box MiniSAT22 from PySAT to find partial solutions quickly.
    r, _ = golombSAT(randF, False)
    r = rulerToBoard(r)
    scoreboard = updateBoard(scoreboard, r)
    print(f"iteration {i + 1}/{numIterations} complete.")

scoreboardTime = time.perf_counter() - scoreboardTime

print(f"Heuristic Generation time: {scoreboardTime} seconds")
# displayBoard(scoreboard)

print("\nFinal Scoreboard:")
print(scoreboard)




'''
CREDITS:
- John Mackey
- Vipin Bhat for the guidance + initial Costas Arrays YEET Session
- https://ieeexplore.ieee.org/document/8261784
- dna ig cause the human genome sequencing project is where i got the idea from

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