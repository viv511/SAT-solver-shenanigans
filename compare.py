from pysat.solvers import Minisat22
from golomb import *
import time

# golomb rulers: (order, length) pairs
rulers = [
    (10, 56),
    (10, 55),
    (11, 75),
    (11, 74),
    (11, 73),
    (11, 72),
    (12, 87),
    (12, 86),
    (12, 85),
]

times = []

trials = 5

for O, L in rulers:
    print(f"Solving for order {O} and length {L}...")    

    # encoding 2
    cumulativeTime = 0.0
    for i in range(trials):
        print(f"\tTrial {i + 1}")

        cnf, _ = encodingTwo(O, L)

        solver = Minisat22()
        solver.append_formula(cnf.clauses)

        start = time.perf_counter()
        res = solver.solve()
        end = time.perf_counter()

        if res:
            model = solver.get_model()
            ruler = getRulerTwo(model, O, L)

            if not verifyRuler(ruler, O):
                print("Invalid ruler found:", ruler)
                exit(1)
        else:
            print("UNSAT... issue with encoding?")
            exit(1)

        cumulativeTime += (end - start)

    times.append((O, L, (cumulativeTime / trials)))

print("\nAll trials completed.\n\n")

# print in a form that can be pasted to a spreadsheet with "\t" as delimiter
print("Solve times:")
print("Order\tLength\tTime (s)")
for O, L, t in times:
    print(f"{O}\t{L}\t{t:.4f}")