//A clause is a disjunction of literals
#pragma once

#include <iostream>
#include <vector>
#include "literal.h"
using namespace std;

using clause = vector<literal>;

val evalClause(clause C, unordered_map<int,bool>& assignments);
void printClause(clause C);
