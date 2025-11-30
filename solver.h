#pragma once

#include <iostream>
#include <unordered_map>
#include "expression.h"
using namespace std;

//DPLL Algorithm!
expression simplify(expression F, int L);
void printAssignments(unordered_map<int,bool>& M);
bool solve(expression F, unordered_map<int,bool>& M, const bool DEBUG_FLAG);
bool unitPropagate(expression& F, unordered_map<int,bool>& M, const bool DEBUG_FLAG);