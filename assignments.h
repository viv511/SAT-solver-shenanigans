#pragma once

#include <iostream>
#include <vector>
using namespace std;

enum class Assignment {
    TRUE,
    FALSE,
    UNASSIGNED
};

vector<Assignment> initialize(int numVars);

