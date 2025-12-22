#pragma once

#include <iostream>
#include <string>
#include "literal.h"
#include "assignments.h"

using namespace std;

void printAssignments(vector<Assignment>& M);

void error(const string& message);

int litToIndex(const literal& l);
bool isTrue(literal l, vector<Assignment>& M);
bool isFalse(literal l, vector<Assignment>& M);
bool isUnassigned(literal l, vector<Assignment>& M);