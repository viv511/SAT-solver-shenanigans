#include "clause.h"
val evalClause(clause C, unordered_map<int,bool>& assignments) {
    bool unassignedLiteral = false;

    for(literal l : C) {
        val v = evalLiteral(l, assignments);

        if(v == val::TRUE) return val::TRUE;
        
        if(v == val::UNASSIGNED) unassignedLiteral = true;
    }

    return unassignedLiteral ? val::UNASSIGNED : val::FALSE;
}

void printClause(clause C) {
    for (size_t i = 0; i < C.size(); i++) {
        printLiteral(C[i]);
        
        if(i != (C.size() - 1)) {
            cout << " v ";
        }
    }
}