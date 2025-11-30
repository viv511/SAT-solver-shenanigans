//An expression is a conjunction of clauses
#pragma once

#include <cmath>
#include <iostream>
#include <vector>
#include "clause.h"
using namespace std;

using expression = vector<clause>;

bool hasEmptyClause(expression& E);
bool compareClauses(clause& c1, clause& c2);
void sortClauses(expression& E);
val evalExpression(expression E, unordered_map<int,bool>& assignments);
void printExpression(expression E);