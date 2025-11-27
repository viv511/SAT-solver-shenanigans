//We will implement the DPLL alg to begin with
#pragma once

#include <iostream>
#include <unordered_map>
#include "expression.h"
using namespace std;

struct DPLL {
    bool solve(expression& F, unordered_map<int,bool>& U);
    bool unitPropagate(expression& F, unordered_map<int,bool>& U);
};