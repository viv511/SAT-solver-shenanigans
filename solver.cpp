//https://en.wikipedia.org/wiki/DPLL_algorithm
//https://www.cs.utexas.edu/~vl/teaching/lbai/dpll.pdf

#include "solver.h"

/*

DPLL(F, U)
    Unit-propagate(F, U);
    if F contains the empty clause then return;
    if F = ⊤ then exit with a model of U;
    L ← a literal containing an atom from F;
    DPLL(F|L, U ∪ {L});
    DPLL(F|L, U ∪ {L})

*/

bool DPLL::solve(expression F, unordered_map<string,bool>& U) {
    unitPropagate(F, U);

}

bool DPLL::unitPropagate(expression F, unordered_map<string,bool>& U) {
    F.sortClauses();

    
}