#include "clause.h"

clause::clause(vector<literal> l) {
    this->literals = l;
}

val clause::eval(const std::unordered_map<std::string,bool>& assignments) {
    bool unassignedLiteral = false;

    for(literal l : literals) {
        val v = l.eval(assignments);

        if(v == val::TRUE) return val::TRUE;
        
        if(v == val::UNASSIGNED) unassignedLiteral = true;
    }

    return unassignedLiteral ? val::UNASSIGNED : val::FALSE;
}

void clause::print() {
    for (size_t i = 0; i < literals.size(); i++) {
        literals[i].print();
        
        if(i < literals.size() - 1) {
            cout << " v ";
        }
    }
}