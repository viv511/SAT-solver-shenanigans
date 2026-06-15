from pysat.solvers import Minisat22
import matplotlib.pyplot as plt
import pandas as pd
from golomb import *
import time

def plotScatterLog(times_list):
    df = pd.DataFrame(times_list, columns=['Order', 'Length', 'Time'])
    
    plt.figure(figsize=(10, 6))
    scatter = plt.scatter(df['Order'], df['Time'], c=df['Length'], 
                cmap='plasma', s=250, edgecolors='black', alpha=0.85)

    plt.yscale('log')
    plt.xticks(sorted(df['Order'].unique()))
    plt.xlabel('Order (marks)', fontsize=12, fontweight='bold')
    plt.ylabel('Avg Search Time (s)', fontsize=12, fontweight='bold')
    plt.title('Golomb Ruler Encoding Efficiency (Log Scale)', fontsize=14, pad=15)

    cbar = plt.colorbar(scatter)
    cbar.set_label('Ruler Length (L)', fontsize=11)

    for i, row in df.iterrows():
        plt.annotate(f"L={int(row['Length'])}", (row['Order'], row['Time']), 
                     xytext=(10, -5), textcoords='offset points', fontsize=9)

    plt.grid(True, which="both", linestyle='--', alpha=0.4)
    plt.tight_layout()
    plt.show()


# times = [
#     (10, 59, 0.5858),
#     (10, 58, 4.0932),
#     (10, 57, 9.6932),
#     (10, 56, 0.4609),
#     (10, 55, 5.1312),
#     (11, 79, 0.7205),
#     (11, 78, 0.3489),
#     (11, 77, 0.8793),
#     (11, 76, 4.8592),
#     (11, 75, 3.5869),
#     (11, 74, 0.9553),
#     (11, 73, 18.7413),
#     (11, 72, 1.1723),
#     (12, 95, 0.0242),
#     (12, 94, 31.8555),
#     (12, 93, 6.1353),
#     (12, 92, 127.0071),
#     (12, 88, 1221.6979)
#     (12, 87, 233.9539),
#     (12, 86, 1040.7657),
#     (12, 85, 69.3870)
# ]
# plotScatterLog(times)
# exit(1)


# golomb rulers: (order, length) pairs
rulers = [
    (12,89), (12, 90),
   (12, 91)
#     (10, 59), (10, 58), (10, 57),
#     (11, 79), (11, 78), (11, 77), (11, 76),
    # (10, 56), (10, 55),
    # (11, 75), (11, 74), (11, 73), (11, 72),
    # (12, 87), (12, 86), (12, 85),
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
        print(f"\t\tTime taken: {end - start:.4f} seconds")

    times.append((O, L, (cumulativeTime / trials)))

print("\nAll trials completed.\n\n")

# print in a form that can be pasted to a spreadsheet with "\t" as delimiter
print("Solve times:")
print("Order\tLength\tTime (s)")
for O, L, t in times:
    print(f"{O}\t{L}\t{t:.4f}")

plotScatterLog(times)


'''
Solve times:
Order   Length  Time (s)
10      56      0.4609
10      55      5.1312
11      75      3.5869
11      74      0.9553
11      73      18.7413
11      72      1.1723
12      87      233.9539
12      86      1040.7657
12      85      69.3870

10      59      0.5858
10      58      4.0932
10      57      9.6932
11      79      0.7205
11      78      0.3489
11      77      0.8793
11      76      4.8592

    Trial 1
            Time taken: 1586.2473 seconds
    Trial 2
            Time taken: 1605.2710 seconds
'''

