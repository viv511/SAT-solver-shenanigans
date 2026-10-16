//An expression is a conjunction of clauses
#pragma once

#include <cmath>
#include <iostream>
#include <vector>
#include "clause.h"
using namespace std;

using expression = vector<watchedClause>;

bool hasEmptyClause(expression& E);
bool compareClauses(watchedClause& wc1, watchedClause& wc2);
void sortClauses(expression& E);
val evalExpression(expression E, unordered_map<int,bool>& assignments);
void printExpression(expression E);