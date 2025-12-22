//A literal is a boolean variable or its negation
#pragma once

#include <iostream>
#include <string>
#include <unordered_map>
#include <cmath>
#include <algorithm>

using namespace std;

//Signed DIMACS-style literals
//i.e. 1 for x1, -1 for ¬x1
using literal = int;

enum class val {
    TRUE,
    FALSE,
    UNASSIGNED
};

inline bool isNeg(literal lit) {
    return lit < 0;
}

inline literal makeNeg(literal lit) {
    return -lit;
}

val evalLiteral(literal L, unordered_map<int,bool>& assignments);
void printLiteral(literal L);