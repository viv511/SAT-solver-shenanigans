//A clause is a disjunction of literals
#pragma once

#include <iostream>
#include <vector>
#include "literal.h"
using namespace std;

struct clause {
    vector<literal> literals;

    clause(vector<literal> l);

    val eval(const std::unordered_map<std::string,bool>& assignments);
    
    void print();
};