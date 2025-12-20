Making my own Boolean SAT (satisfiable) Solver!

# Motivation:

I heard about SAT solvers from our Discrete Math class @ CMU (15-151) taught by Dr. John Mackey and Dr. William Kuszmaul! I went on a little deep-dive into how they work and eventually decided to try to make my own. This log serves a progress tracker for myself and a place to record all the advancements/tricks/tips I've learned.

# Version 0 (Basic DPLL Solver):

Started: 11.21.25 ==> Ended: 11.30.25

### 11.22.25

Started setting up infrastructure of the code, mainly how expressions will form in CNF form. Literals, clauses, and expressions. Implementing DPLL after reading the literature, have to set up unit propagation.

### 11.26.25

Started implementing the DPLL algorithm. Implemented DIMACS-style variable names for literals

### 11.27.25

Made parsing work! Able to input a string and have it create and expression and sort it based on clause length.

### 11.30.25

SUCCESS! Version 0 is complete!! The SAT solver works on a variety of tests and is even faster then a few sites that I've seen. Theres a lot of room for improvement though, especially in terms of space allocation and backtracking. There is definitely a more elegant way to approach it, so I'm going to spend more time reading about other successful solvers and try to incorporate what they do into my own. I think I need to move on from the DPLL approach though. I'll also go talk to Daniel to see how their group were able to generate Costas Arrays and actually run their solver on it.

# Version 0.5 (minor improvements to DPLL)

### 12.1.25 - 12.12.25

Finals Week prep, didn't get much done

### 12.15.25 - 12.17.25

Did a lot of reading on SAT Solvers, particularly optimizations and how to start benchmarking my own sat solver with a .cnf format.

### 12.18.25

Implemented proper DIMACS file reading, specifically so that I can test my sat solver against the online .cnf files on the sat solver benchmark websites. With the # of variables and clauses given, we can move the unordered map into an array for much faster performance.

HUGE SPEED UP ALREADY!!

**_Testing uf250-01 from the benchmarks_**

1. Time to solve: 33.8272 seconds
2. Time to solve: 35.0956 seconds
3. Time to solve: 33.1517 seconds
   AVG: 34.025 seconds!

benchmarks/uf250-02.cnf --- Time to solve: ???? (DNF)

### 12.19.25

Did a lot more theory/reading work on Two-Watched literals. The concept of no work & O(1) being different was kind of interesting to think about. I think I've always assumed O(1) was "basically nothing" but basically nothing != nothing, which makes a lot of sense.

I'll need to implement a watchlist of some sort for every single clause thats in our expression. Maybe a task for tomorrow?

# TO-DO:

- Read about the two watched literals approach and implement that to reduce space/time complexity
- Benchmark tests, make it accept p cnf X Y form dimacs style input

<!-- Credits/References -->

- Dr. Marijn Heule / Dr. John Mackey for the initial inspiration
- Various YT lectures and recordings the intuition and basics of SAT solvers
- https://jix.github.io/varisat/manual/0.2.0/formats/dimacs.html
- https://www.cs.cmu.edu/~wcohen/15451-f10/lectures/dpll.pdf
- https://homes.cs.washington.edu/~kevinz/sat-solver/ (for initial verification/comparison speed-wise)
- https://en.wikipedia.org/wiki/DPLL_algorithm
- https://www.cs.utexas.edu/~vl/teaching/lbai/dpll.pdf
- https://codingnest.com/modern-sat-solvers-fast-neat-underused-part-1-of-n/ (lovely resource)
- https://school.a4cp.org/summer2011/slides/Gent/SATCP3.pdf
- https://cse.unl.edu/~choueiry/S17-235H/files/SATslides07.pdf
- https://ceur-ws.org/Vol-3201/paper2.pdf
