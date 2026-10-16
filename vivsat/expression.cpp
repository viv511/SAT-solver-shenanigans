#include "expression.h"

bool hasEmptyClause(expression& E) {
    if(E.empty()) return false;
    for(watchedClause& wc : E) {
        if(wc.empty()) {
            return true;
        }
    }
    return false;
}

//Make a custom comparator to sort clauses in an expression by size
bool compareClauses(watchedClause& wc1, watchedClause& wc2) {
    return wc1.size() < wc2.size();
}

void sortClauses(expression& E) {
    sort(E.begin(), E.end(), compareClauses);
}

val evalExpression(expression E, unordered_map<int,bool>& assignments) {
    bool hasUnassigned = false;

    for(watchedClause& wc : E) {
        val v = evalClause(wc.C, assignments);

        if(v == val::FALSE) return val::FALSE;

        if(v == val::UNASSIGNED) hasUnassigned = true;
    }

    return hasUnassigned ? val::UNASSIGNED : val::TRUE;
}

void printExpression(expression E) {
    for(size_t i = 0; i < E.size(); i++) {
        cout << "(";
        printClause(E[i].C);
        cout << ")";

        if(i < E.size() - 1) {
            cout << " ∧ ";
        }
    }

    cout << endl;
}