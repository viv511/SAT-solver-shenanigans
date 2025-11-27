#include "expression.h"

//Make a custom comparator to sort clauses in an expression by size
bool compareClauses(clause& c1, clause& c2) {
    return c1.size() < c2.size();
}

void sortClauses(expression& E) {
    sort(E.begin(), E.end(), compareClauses);
}


val evalExpression(expression E, unordered_map<int,bool>& assignments) {
    bool hasUnassigned = false;

    for(clause C : E) {
        val v = evalClause(C, assignments);

        if(v == val::FALSE) return val::FALSE;

        if(v == val::UNASSIGNED) hasUnassigned = true;
    }

    return hasUnassigned ? val::UNASSIGNED : val::TRUE;
}

void printExpression(expression E) {
    for(size_t i = 0; i < E.size(); i++) {
        cout << "(";
        printClause(E[i]);
        cout << ")";

        if(i < E.size() - 1) {
            cout << " ∧ ";
        }
    }

    cout << endl;
}