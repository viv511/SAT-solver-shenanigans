#include <iostream>
#include "literal.h"
#include "clause.h"
#include "expression.h"
#include "solver.h"
#include <sstream>
using namespace std;

expression parseInputString(string s) {
    //String: (x ∨ y ∨ ¬z) ∧ (¬y ∨ z) as
    //SAMPLE INPUT "1 2 -3 0 -2 3 0"

    expression F;
    clause c;

    stringstream ss(s);
    int lit;

    while(ss >> lit) {
        if(lit == 0) {
            F.push_back(c);
            c.clear();
        } else {
            c.push_back(lit);
        }
    }

    return F;
}

int main() {
    // expression F{{c1, c2, c3, c4, c5}};
    expression F = parseInputString("-1 -2 0 2 3 0 -2 -3 0 1 0 1 -2 0");
    unordered_map<int, bool> U;
    
    printExpression(F);

    DPLL solver;
    solver.solve(F, U);

    printExpression(F);
}