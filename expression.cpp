#include "expression.h"

expression::expression(vector<clause> e) {
    this->exp = e;
}

//Make a custom comparator to sort clauses by size
bool compareClauses(clause c1, clause c2) {
    return c1.literals.size() < c2.literals.size();
}

void expression::sortClauses() {
    sort(exp.begin(), exp.end(), compareClauses);
}

val expression::eval(const std::unordered_map<std::string,bool>& assignments) {
    bool hasUnassigned = false;

    for(clause c : exp) {
        val v = c.eval(assignments);

        if(v == val::FALSE) return val::FALSE;

        if(v == val::UNASSIGNED) hasUnassigned = true;
    }

    return hasUnassigned ? val::UNASSIGNED : val::TRUE;
}

void expression::print() {

    for (size_t i = 0; i < exp.size(); i++) {
        cout << "(";
        exp[i].print();
        cout << ")";

        if(i < exp.size() - 1) {
            cout << " ∧ ";
        }
    }

    cout << endl;
}