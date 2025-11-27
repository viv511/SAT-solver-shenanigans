#include <iostream>
#include "literal.h"
#include "clause.h"
#include "expression.h"
#include "solver.h"
using namespace std;

expression parseInputString(string s) {
    //String: (x ∨ y ∨ ¬z) ∧ (¬y ∨ z) as
    //SAMPLE INPUT "1 2 -3 0 -2 3 0"

    expression F{{}};
    clause c{{}};

    size_t pos = 0;
    
    // while((pos = s.find(" ")) != string::npos) {
    //     literal lit = stoi(s.substr(0, pos));
    //     s.erase(0, pos + 1);

    //     if(lit == 0) {
    //         F.push_back(c);
    //         c = clause{{}};
    //     } else {
    //         c.push_back(lit);
    //     }
    // }

    return F;
}

int main() {
    // expression F{{c1, c2, c3, c4, c5}};
    expression F = parseInputString("1 2 -3 0 -2 3 0");
    unordered_map<int, bool> U;
    printExpression(F);
}