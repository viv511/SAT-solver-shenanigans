//An expression is a conjunction of clauses
#pragma once

#include <cmath>
#include <iostream>
#include <vector>
#include "clause.h"
using namespace std;

using expression = vector<clause>;

void sortClauses(expression E);
val evalExpression(expression E, unordered_map<int,bool>& assignments);
void printExpression(expression E);