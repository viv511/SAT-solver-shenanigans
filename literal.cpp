#include "literal.h"

literal::literal(string s, bool n) {
    this->name = s;
    this->negated = n;
}

val literal::eval(const unordered_map<string,bool>& assignments) {
    auto it = assignments.find(name);
    
    if(it == assignments.end()) return val::UNASSIGNED;

    bool assignedValue = it->second;
    
    //Negate if needed
    assignedValue = negated ? !assignedValue : assignedValue; 

    return assignedValue ? val::TRUE : val::FALSE;
}

void literal::print() {
    std::cout << (negated ? "¬" : "") << name;
}
