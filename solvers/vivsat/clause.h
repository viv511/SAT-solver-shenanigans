#pragma once

#include <iostream>
#include <vector>
#include "literal.h"
#include "utils.h"

using namespace std;

using clause = vector<literal>;

struct watchedClause {
    clause C;
    uint w1Index;
    uint w2Index;

    watchedClause(clause C) {
        this->C = C;
        
        if(C.size() >= 2) {
            this->w1Index = 0;
            this->w2Index = 1;
        }
        else if(C.size() == 1) {
            this->w1Index = 0;
            this->w2Index = 0;
        }
        else {
            //TODO shouldnt this never happen? AKA UNSAT when empty clause?
            error("WATCHED CLAUSE ERROR: Empty clause found!");
        }

        //POST: C.size() >= 1
    }
    
    size_t size() const {
        return this->C.size();
    }

    bool empty() const {
        return this->C.empty();
    }

    bool isUnit() const {
        return this->C.size() == 1;
    }

    literal getW1() const {
        return this->C[this->w1Index];
    }

    literal getW2() const {
        return this->C[this->w2Index];
    }

    literal getOtherWatch(literal l) const {
        //PRE: l is one of the watched literals
        if(l == getW1()) return getW2();
        return getW1(); //assume l == getW2()
    }

    void moveWatch(literal oldLiteral, int newIndex) {
        if(oldLiteral == getW1()) {
            this->w1Index = newIndex;
        } else if(oldLiteral == getW2()) {
            this->w2Index = newIndex;
        } else {
            error("WATCHED CLAUSE ERROR: moveWatch called on non-watched literal");
        }
    }
};

val evalClause(clause C, unordered_map<int,bool>& assignments);
void printClause(clause C);
