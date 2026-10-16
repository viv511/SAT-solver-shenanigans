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

# CONSTANTS
# K_n: star-parity relaxation, at most k crossings
# n = 9
# k = 36
n = 8
k = 18

# For scorecard generation
THRESHOLD = 10
NUM_ITERATIONS = 5
PCT_RAND = 95
TRUE_WEIGHT = 7
FALSE_WEIGHT = 2

# More positive the board, the more likely it is to be true (vice versa!)
def updateBoard(inputBoard, updateBoard):
   for i in range(len(inputBoard)):
      if updateBoard[i] > 0:
         inputBoard[i] += TRUE_WEIGHT
      else:
         inputBoard[i] -= FALSE_WEIGHT
   return inputBoard

def solveModified(cnf, cnfFile):
   with open(cnfFile, "w") as f:
      cnf.to_fp(f)

   result, elapsed = solveLocalModified(cnfFile)
   model = modelFromResult("result.out")

   return model, elapsed, result.stderr.strip()

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

   for i in range(NUM_ITERATIONS):
      randF = CNF()
      randF.extend(baseClauses)

      # select random subset of constraint clauses
      sampled = random.sample(additionalClauses, int(len(additionalClauses) * PCT_RAND / 100))
      randF.extend(sampled)

      model, _, _ = solveModified(randF, "Fsubset.cnf")

      assignmentFromSubset = crossingToBoard(model, length)

      # takes a alpha assignment for the partial CNF and updates scorecard via the weights
      scorecard = updateBoard(scorecard, assignmentFromSubset)

      # nice looking progress bar because why not
      done = int((i + 1) / NUM_ITERATIONS * progressBarLen)
      bar = "#" * done + "-" * (progressBarLen - done)
      print(f"\r[{bar}]", end="", flush=True)

   end = time.perf_counter()
   generationTime = end - start

   print(" Generation done!\n")

   return scorecard, generationTime

def writeScorecard(path, threshold, variables, scores):
   with open(path, "w") as f:
      f.write(f"{threshold}\n")
      for var, score in zip(variables, scores): #woah zip in the wild W 150
          f.write(f"{var} {score}\n")

if __name__ == "__main__":
   F, base, varCount = encodeCrossing(n, k)
   print(f"n = {n}, k = {k}")
   print(f"total clauses: {len(F.clauses)}")
   print(f"└──> base clauses: {base}, additional clauses: {len(F.clauses) - base}\n")

   # BASELINE SOLVE (empty scorecard ==> plain minisat)
   writeScorecard("scorecard.txt", 0, [], [])
   model, normalSolveTime, solverLog = solveModified(F, "crossing.cnf")

   print(f"Time to solve: {normalSolveTime} seconds")
   print(solverLog)

   # GENERATING HEURISTIC SCORECARD
   scorecard, heuristicTime = generateScorecard(varCount, F.clauses[:base], F.clauses[base:])
   writeScorecard("scorecard.txt", THRESHOLD, range(1, varCount + 1), scorecard)
   print("# of variables above threshold: ", sum(1 for s in scorecard if abs(s) > THRESHOLD))

   # HEURISTIC SOLVE
   model, heuristicSolveTime, solverLog = solveModified(F, "crossing.cnf")

   print(solverLog)

   print("\nNORMAL SOLVE TIME:\t\t\t", normalSolveTime)
   print("HEURISTIC SOLVE TIME:\t\t\t", heuristicSolveTime + heuristicTime)
   print("└──> SPLIT:\t\t\t\t", heuristicTime, "+", heuristicSolveTime, "\n")