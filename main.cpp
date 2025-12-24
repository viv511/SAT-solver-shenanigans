#include <iostream>
#include <chrono>
#include "assignments.h"
#include "clause.h"
#include "expression.h"
#include "literal.h"
#include "solver.h"
#include "2WL_solver.h"
#include <sstream>
#include <fstream>

using namespace std;

expression parseCNF(string filename) {
    //TODO error when the file name doesnt exist or is empty
    expression F;
    clause c;

    //Read file
    ifstream infile(filename);
    string s;

    //P-line
    bool foundPLine = false;
    string p;
    string cnf;

    while (getline(infile, s)) {
        stringstream ss(s);

        if(s.empty() || s[0] == 'c') continue; //ignore comments + empty lines

        if(s[0] == 'p') {
            if(foundPLine) error("Multiple p-lines found");
            foundPLine = true;
            ss >> p >> cnf >> NUM_VARS >> NUM_CLAUSES;

            if(p != "p" || cnf != "cnf" || NUM_VARS < 1 || NUM_CLAUSES < 1) {
                error("Invalid p-line");
            }

            F.reserve(NUM_CLAUSES);
            continue;
        }

        int lit;
        
        while (ss >> lit) {
            if (lit == 0) {
                if (!c.empty()) {
                    F.push_back(watchedClause(c));
                    c.clear();
                }
            } else {
                c.push_back(lit);
            }
        }
    }

    //redundant check just in case no trailing 0
    if (!c.empty()) {
        F.push_back(watchedClause(c));
    }

    if(F.empty()) error("Empty expression found");
    if(!foundPLine) error("No p-line found");
    
    return F;
}

vector<vector<int>> initializeWatchlist(expression& F, int nV) {
    vector<vector<int>> WL(2 * nV);

    for(size_t i = 0; i < F.size(); i++) {
        watchedClause& wc = F[i];
        literal w1 = wc.getW1();
        literal w2 = wc.getW2();

        WL[litToIndex(w1)].push_back(i);
        if(w1 != w2) {
            WL[litToIndex(w2)].push_back(i);
        }
    }

    return WL;
}

const bool DEBUG_FLAG = true;

bool verifyAssignment(expression& F, vector<Assignment>& M) {
    for(int i = 0; i < F.size(); i++) {
        watchedClause& wc = F[i];
        bool clauseSatisfied = false;
        for(literal l : wc.C) {
            if(isTrue(l, M)) {
                clauseSatisfied = true;
                break;
            }
        }
        if(!clauseSatisfied) {
            cout << "Clause " << i << " not satisfied: (";
            for(literal l : wc.C) {
                cout << l << " ";
            }
            cout << ")\n";
            cout << "Assignments: ";
            for(literal l : wc.C) {
                int v = abs(l);
                cout << "v" << v << "=" << (M[v] == Assignment::TRUE ? "T" : (M[v] == Assignment::FALSE ? "F" : "U")) << " ";
            }
            cout << "\n";
            return false;
        }
    }
    return true;
}

int main() {
    // expression CNF_expr = parseCNF("benchmarks/uf20-0100.cnf");
    expression CNF_expr = parseCNF("benchmarks/uf250-02.cnf");
    expression copy = CNF_expr; //copy for later verification
    
    vector<Assignment> map = initializeAssignment(NUM_VARS);
    vector<vector<int>> wList = initializeWatchlist(CNF_expr, NUM_VARS);
    literalTrail trail; //empty trail to start
    vector<int> decisionLevel; //track decision levels
    decisionLevel.push_back(0); //initial level 0

    //EXPRESSION TO SOLVE:
    cout << "Solving an expression with " << NUM_VARS << " variables and " << NUM_CLAUSES << " clauses:\n";
    if(DEBUG_FLAG) {
        printExpression(CNF_expr);
    }

    cout << "\n---------------------------------------------------\n";


    //TIME TO SOLVE / FIND UNSAT
    auto start = chrono::high_resolution_clock::now();
    

    // bool ans = solve(CNF_expr, map, DEBUG_FLAG); // DPLL
    bool ans = solve2WL(CNF_expr, map, wList, trail, decisionLevel, DEBUG_FLAG); //2WL
    if(!ans) cout << "UNSAT\n";

    auto finish = chrono::high_resolution_clock::now();

    chrono::duration<double> elapsed = finish - start;
    cout << "\nTime to solve: " << elapsed.count() << " seconds" << endl;

    bool verified = verifyAssignment(copy, map);
    if(ans && !verified) {
        cout << "\nERROR: Assignment does not satisfy expression!\n";
    }
    else if(ans){
        cout << "\nVerified: Assignment satisfies expression.\n";
    }
    return 0;
}