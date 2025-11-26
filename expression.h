//An expression is a conjunction of clauses
#pragma once

#include <iostream>
#include <vector>
#include "clause.h"
using namespace std;

struct expression {
    vector<clause> exp;

    expression(vector<clause> e);
    void sortClauses();
    val eval(const std::unordered_map<std::string,bool>& assignments);
    void print();
};