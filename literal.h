//A literal is a boolean variable or its negation
#pragma once

#include <iostream>
#include <string>
#include <unordered_map>
using namespace std;

enum class val {
    TRUE,
    FALSE,
    UNASSIGNED
};

struct literal {
    string name;
    bool negated;

    literal(string s, bool n);
    val eval(const unordered_map<string,bool>& assignments);

    void print();
};