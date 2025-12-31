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

# Version 1 (2-Watched Literals Scheme + minor improvements)

Started: 12.1.25 ==> Ended: ???

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

### 12.20.25

Improved the clause struct slightly by adding the basics of a watch list to it.

### 12.21.25

"Implemented" the two watched literals method (but need to test it and figure out what the bugs are...)

### 12.22.25

Fixed and implemented **a fully working two watched literals** method. Changed propagation method to queue based (BFS-style) rather than naive recursion. I also implemented a Clause-based heuristic that attacks smaller length clauses first.

This greatly improved performance on the initial test that I was using "uf250-01." The average time to compute this is now around 1-2 seconds, which is insane. It's making steady progress on the other "uf250-02" that it DNF'd before, but this still doesn't seem the best.

I think I need to play the optimization game some more, especially with this thing called "VSIDS" and CDCL. CDCL is the most viable next option, especially since it leads to less backtracking which is better for me.

### 12.23.25

VSIDS implementation was unsuccessful, but I spent a lot of time setting up the CDCL structure and backbone by going from trails as a vector of int to a vector of TrailEntry's. I also fixed some issues of duplicate propagates, which might have been the cause of the "hanging" that I was experiencing earlier. I'm really really happy with the current results---even though I haven't finished implementing full CDCL yet.

Current Benchmarks:

- CAN solve the sudoku.cnf file I got from (insert website), took 0.029 seconds
- uf250-01 ==> 0.003 seconds
- uf250-01 ==> 0.002

WOW! I need to make sure this isn't a bug though...

VERIFYING uf250-067:

- Time: ~0.002 seconds

My result: SAT v -1 2 3 -4 -5 -6 -7 8 9 10 -11 -12 14 15 16 -17 -18 -19 -20 22 -23 -24 25 -26 -27 -28 -29 30 -31 -32 -33 -34 -35 36 -37 38 -39 -41 42 43 -44 45 46 47 -48 -49 -50 51 -52 -53 -54 -55 -56 57 58 -59 -60 -61 62 -63 64 65 66 67 -68 -69 70 71 -72 73 -74 75 -76 -77 -78 79 80 -81 -83 84 -85 87 -88 89 90 91 92 -93 94 95 -96 97 -98 -99 100 -101 102 -103 -104 -105 106 107 -108 109 110 -111 -112 -113 -114 -115 -116 -117 -118 -119 120 -121 -122 -123 -124 -125 -126 -127 -128 129 130 -131 132 -133 -134 -135 -136 137 138 -139 -140 141 -142 -143 144 145 146 -147 -148 149 -150 151 -152 153 -154 155 -156 157 -158 159 -160 161 162 163 164 165 -166 -167 -168 -169 170 -171 172 173 -174 -175 -176 -177 -178 -179 -180 181 182 -183 -184 185 -186 -187 -188 -189 -190 191 192 -193 194 195 196 -197 -198 199 200 201 -202 -203 -204 -205 -206 207 -208 -209 210 -211 212 213 -214 215 216 217 218 -219 220 221 222 -223 -224 -225 226 -227 228 229 -230 -231 232 233 234 -235 236 -237 -238 239 -240 241 -242 -243 244 245 246 -247 248 249 250

Comparing with a working SAT solver:
**_"ERROR: Assignment does not satisfy expression!"_**

Upon further inspection (I added a verifier that plugs the values back in (should have done this a long time ago)), it seems that my SAT solver actually returns bogus values. So... the debugging continues

3.5 hours later, still debugging code that should be working...

I think I need to take a break from the code, go and read the theory again and write this from scratch again.

Deleting all the changes, reverting back to last commit.

### 12.30.25

Code refactoring + cleaning up

# TO-DO:
- make nicer CNF reading dimacs file
- Possible steps for the future:
  - ~~DPLL Algorithm~~
  - ~~DIMACS style input~~
  - ~~Optimizations (Map --> Vector)~~
  - ~~Two-watched literals~~
  - ~~Queue-based propagation~~
  - Clause learning (CDCL)
  - VSIDS branching heuristic
  - Add a make file (c++ things)
  - Restarts
  - Memory layout optimizations

<!-- Credits/References -->

- Dr. Marijn Heule / Dr. John Mackey for the initial inspiration
- Various YT lectures and recordings the intuition and basics of SAT solvers
- https://users.aalto.fi/~tjunttil/2020-DP-AUT/notes-sat/overview.html
- https://jix.github.io/varisat/manual/0.2.0/formats/dimacs.html
- https://www.cs.cmu.edu/~wcohen/15451-f10/lectures/dpll.pdf
- https://homes.cs.washington.edu/~kevinz/sat-solver/ (for initial verification/comparison speed-wise)
- https://en.wikipedia.org/wiki/DPLL_algorithm
- https://www.cs.utexas.edu/~vl/teaching/lbai/dpll.pdf
- https://codingnest.com/modern-sat-solvers-fast-neat-underused-part-1-of-n/ (lovely resource)
- https://school.a4cp.org/summer2011/slides/Gent/SATCP3.pdf
- https://cse.unl.edu/~choueiry/S17-235H/files/SATslides07.pdf
- https://ceur-ws.org/Vol-3201/paper2.pdf
- https://simewu.com/SAT-solver/ (for examples?)

Currently Reading: SAT/SMT by example --- Progress: Page 1/720
