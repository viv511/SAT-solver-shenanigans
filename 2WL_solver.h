#pragma once

#include <iostream>
#include "expression.h"
#include "assignments.h"
#include <cassert>
#include "utils.h"

using namespace std;

using literalTrail = vector<int>;

int findUnassigned(vector<Assignment>& M);
void assign(int l, vector<Assignment>& M, literalTrail& trail);
void undo(vector<Assignment>& M, literalTrail& trail, int target);
bool propogate(int falsifiedLiteral, vector<Assignment>& M, vector<vector<int>>& wList, literalTrail& trail, expression& F);

bool solve2WL(expression& F, vector<Assignment>& M, vector<vector<int>>& wList, literalTrail& trail, vector<int>& decisionLevel, bool DEBUG);