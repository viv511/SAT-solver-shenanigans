#pragma once

#include <iostream>
#include "expression.h"
#include "assignments.h"

using namespace std;

//DPLL Algorithm!
expression simplify(expression F, int L);
void printAssignments(vector<Assignment>& M);
bool solve(expression F, vector<Assignment>& M, const bool DEBUG_FLAG);
bool unitPropagate(expression& F, vector<Assignment>& M, const bool DEBUG_FLAG);