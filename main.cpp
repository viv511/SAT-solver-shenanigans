#include <iostream>
#include "literal.h"
#include "clause.h"
#include "expression.h"
using namespace std;

int main() {
    literal x1("p", false);
    literal x2("p", true);
    literal x3("q", false);
    literal x4("q", true);
    literal x5("r", false);
    literal x6("r", true);

    clause c1{{x1}}; //p
    clause c2{{x1, x3}}; //p v q
    clause c3{{x2, x4}}; //¬p v ¬q
    clause c4{{x3, x5}}; //q v r
    clause c5{{x4, x6}}; //¬q v ¬r

    expression F{{c1, c2, c3, c4, c5}};
    unordered_map<string, bool> U;
    F.print();
}