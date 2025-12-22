#pragma once

#include <iostream>
#include "expression.h"
#include "assignments.h"

using namespace std;

expression simplify(expression F, int L);
bool solve(expression F, vector<Assignment>& M, const bool DEBUG_FLAG);
bool unitPropagate(expression& F, vector<Assignment>& M, const bool DEBUG_FLAG);