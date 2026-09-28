"""
crossing.py  n  k  >  file.cnf
DIMACS CNF that is satisfiable iff the parity constraints derived from the
star observation admit an assignment with at most k crossings in K_n.

Adopted from code provided by Dr. Mackey, with minor modifications to separate clauses
into base and additional clauses for the purpose of generating a heuristic scorecard.

using "star-parity relaxation"
"""

import itertools
import time
import random
import subprocess

from pysat.formula import CNF
from pysat.solvers import Minisat22

# CONSTANTS
# K_n: star-parity relaxation, at most k crossings
n = 8
k = 18

# For scorecard generation
numIterations = 5
pctRandom = 90
trueWeightage = 7
falseWeightage = 2

def updateBoard(inputBoard, updateBoard):
   for i in range(len(inputBoard)):
      if updateBoard[i] > 0:
         inputBoard[i] += trueWeightage
      else:
         inputBoard[i] -= falseWeightage
   return inputBoard

def solve(cnf):
   solver = Minisat22()
   solver.append_formula(cnf.clauses)
   res = solver.solve()
   model = solver.get_model() if res else None
   solver.delete()
   return res, model

def encodeCrossing(n, k):
   m = n - 1
   var = {}
   baseClauses = []

   def v(key):
      if key not in var:
         var[key] = len(var) + 1
      return var[key]

   def xor(lits, parity):
      # forbid any `lits` assignment that has the wrong parity
      for bits in itertools.product([0, 1], repeat=len(lits)):
         if sum(bits) % 2 != parity:
               baseClauses.append([-l if b else l for l, b in zip(lits, bits)])

   # BASE CLAUSES
   for a, b, c, d in itertools.combinations(range(m), 4):
      for (e0, e1), (f0, f1) in (((a, b), (c, d)), ((a, c), (b, d)), ((a, d), (b, c))):
         interleave = int((e0 < f0 < e1) != (e0 < f1 < e1))
         xor([v(('t', e0, e1, f0, f1)),
               v(('s', f0, e0, e1)), v(('s', f1, e0, e1)),
               v(('s', e0, f0, f1)), v(('s', e1, f0, f1))], interleave)

   baseVarCount = len(var)

   # ADDITIONAL CLAUSES
   additionalClauses = []
   crossings = list(var.values())
   r = {}

   def R(i, j):
      return r.setdefault((i, j), baseVarCount + len(r) + 1)

   for i, x in enumerate(crossings):
      if k == 0:
         additionalClauses.append([-x])
         continue
      additionalClauses.append([-x, R(i, 1)])
      if i > 0:
         for j in range(2, k + 1):
               additionalClauses.append([-x, -R(i - 1, j - 1), R(i, j)])
         for j in range(1, k + 1):
               additionalClauses.append([-R(i - 1, j), R(i, j)])
         additionalClauses.append([-x, -R(i - 1, k)])

   cnf = CNF()
   cnf.extend(baseClauses)
   cnf.extend(additionalClauses)

   return cnf, len(baseClauses), baseVarCount

def crossingToBoard(model, baseVarCount):
   return [1 if lit > 0 else -1 for lit in model[:baseVarCount]]

def solveLocalModified(cnfFile):
   start = time.perf_counter()
   result = subprocess.run(
         ["./modifiedMinisat/build/release/bin/minisat", cnfFile, "result.out"],
         capture_output=True,
         text=True
      )
   end = time.perf_counter()

   return result, end - start

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

def countCrossings(model, varCount):
   return [x for x in model if x > 0 and x <= varCount]

def generateScorecard(length, baseClauses, additionalClauses):
   progressBarLen = 30  # just because i like looking at nice looking progress bars
   scorecard = [0.0] * length

   start = time.perf_counter()

   for i in range(numIterations):
      randF = CNF()
      randF.extend(baseClauses)

      # Select random subset of constraint clauses
      sampled = random.sample(additionalClauses, int(len(additionalClauses) * pctRandom / 100))
      randF.extend(sampled)

      res, model = solve(randF)
      if not res:
         print(f"\nwarning: subinstance {i} was UNSAT (IMPOSSIBLE!!)")
         exit(1)

      assignmentFromSubset = crossingToBoard(model, length)

      # Takes a alpha assignment for the partial CNF and updates scorecard via the weights
      scorecard = updateBoard(scorecard, assignmentFromSubset)

      # nice looking progress bar because why not
      done = int((i + 1) / numIterations * progressBarLen)
      bar = "#" * done + "-" * (progressBarLen - done)
      print(f"\r[{bar}] {i + 1}/{numIterations}", end="", flush=True)

   end = time.perf_counter()
   generationTime = end - start

   print("Generation done!\n")

   return scorecard, generationTime

F, base, varCount = encodeCrossing(n, k)
print(f"total clauses: {len(F.clauses)}")
print(f"└──> base clauses: {base}, additional clauses: {len(F.clauses) - base}\n")

with open("crossing.cnf", "w") as f:
   F.to_fp(f)

solver = Minisat22()
solver.append_formula(F.clauses)

start = time.perf_counter()
res = solver.solve()
end = time.perf_counter()
normalSolveTime = end - start

if res:
   print("SAT")
   model = solver.get_model()
   crossings = [x for x in model if x > 0 and x <= varCount]
   print(f"crossings: {len(crossings)}")
else:
   print("UNSAT... issue with encoding?")
   exit(1)

print(f"Time to solve: {normalSolveTime} seconds")
solver.delete()

# GENERATING HEURISTIC SCORECARD
print(f"\nbase clauses: {base}, additional clauses: {len(F.clauses) - base}\n")
scorecard, heuristicTime = generateScorecard(varCount, F.clauses[:base], F.clauses[base:])
# print(len(scorecard), "\n", scorecard)
print(f"\nScorecard generation time: {heuristicTime} seconds")

# MODIFIED MINISAT SOLVE
_, heuristicSolveTime = solveLocalModified("crossing.cnf")
model = modelFromResult("result.out")
crossingsHeuristic = countCrossings(model, varCount)

print(f"crossings (heuristic): {len(crossingsHeuristic)}")

print("\nNORMAL SOLVE TIME:\t\t\t", normalSolveTime)
print("HEURISTIC SOLVE TIME:\t\t\t", heuristicSolveTime + heuristicTime)
print("└──> SPLIT:\t\t\t\t", heuristicTime, "+", heuristicSolveTime, "\n")