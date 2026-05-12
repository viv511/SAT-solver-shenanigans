#include "literal.h"

int litToIndex(const literal& l) {
    return 2 * (abs(l) - 1) + ((l < 0) ? 1 : 0);
}

val evalLiteral(literal L, unordered_map<int,bool>& assignments) {
	cout << "WE ARE USING THIS BTW";
	int id = abs(L);
	auto it = assignments.find(id);
	
	//Missing in map ==> UNASSIGNED
	if(it == assignments.end()) return val::UNASSIGNED;

	bool assignedValue = it->second;

	// Negate if literal is negative
	if(isNeg(L)) assignedValue = !assignedValue;

	return assignedValue ? val::TRUE : val::FALSE;
}

void printLiteral(literal L) {
	std::cout << (isNeg(L) ? "¬" : "") << abs(L);
}
