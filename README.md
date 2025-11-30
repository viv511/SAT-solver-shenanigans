Making my own Boolean SAT (satisfiable) Solver!

# Version 0:
Started: 11/21/25
Ended: N/A

## Log:
TODO:
- Think about const and type safety w/ "const" after print

### 11.22.25
Started setting up infrastructure of the code, mainly how expressions will form in CNF form.
Literals, clauses, and expressions. Implementing DPLL after reading the literature, have to set up unit propagation.

### 11.26.25
Started implementing the DPLL algorithm
Implemented DIMACS-style variable names for literals

### 11.27.25
Made parsing work! Able to input a string and have it create and expression and sort it based on clause length.

### 11.30.25
SUCCESS! Version 0 is complete! :) The SAT solver works on a variety of tests and is even faster then a few sites that I've seen. Theres a lot of room for improvement though, especially in terms of space allocation and backtracking. There is definitely a more elegant way to approach it, so I'm going to spend more time reading about other successful solvers and try to incorporate what they do into my own. I think I need to move on from the DPLL approach though. I'll also go talk to Daniel to see how their group were able to generate Costas Arrays and actually run their solver on it.

TODO: Read about the two watched literals approach and implement that to reduce space/time complexity

<!-- Credits/References -->
- Dr. Marijn Heule / Dr. John Mackey for the initial inspiration
- Various YT lectures and recordings the intuition and basics of SAT solvers
- https://jix.github.io/varisat/manual/0.2.0/formats/dimacs.html
- https://www.cs.cmu.edu/~wcohen/15451-f10/lectures/dpll.pdf
- https://homes.cs.washington.edu/~kevinz/sat-solver/ (for initial verification/comparison speed-wise)
- https://en.wikipedia.org/wiki/DPLL_algorithm
- https://www.cs.utexas.edu/~vl/teaching/lbai/dpll.pdf