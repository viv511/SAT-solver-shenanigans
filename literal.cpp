#include "literal.h"

val evalLiteral(literal L, unordered_map<int,bool>& assignments) {
	int id = absIndex(L);
	auto it = assignments.find(id);
	
	//Missing in map ==> UNASSIGNED
	if(it == assignments.end()) return val::UNASSIGNED;

	bool assignedValue = it->second;

	// Negate if literal is negative
	if(isNeg(L)) assignedValue = !assignedValue;

	return assignedValue ? val::TRUE : val::FALSE;
}

void printLiteral(literal L) {
	std::cout << (isNeg(L) ? "¬" : "") << absIndex(L);
}
