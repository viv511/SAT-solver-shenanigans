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

tuple<expression, int, int> parseCNF(string filename) {
    int numVars = 0;
    int numClauses = 0;

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
            ss >> p >> cnf >> numVars >> numClauses;

            if(p != "p" || cnf != "cnf" || numVars < 1 || numClauses < 1) {
                error("Invalid p-line");
            }

            F.reserve(numClauses);
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
    
    return {F, numVars, numClauses};
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

int main() {
    // tuple<expression, int, int> data = parseCNF("benchmarks/uf20-01000.cnf");
    tuple<expression, int, int> data = parseCNF("benchmarks/uf250-01.cnf");

    expression CNF_expr = get<0>(data);

    int numVars = get<1>(data);
    int numClauses = get<2>(data);

    vector<Assignment> map = initializeAssignment(numVars);
    vector<vector<int>> wList = initializeWatchlist(CNF_expr, numVars);
    literalTrail trail;
    vector<int> decisionLevel;

    //EXPRESSION TO SOLVE:
    cout << "Solving an expression with " << numVars << " variables and " << numClauses << " clauses:\n";
    printExpression(CNF_expr);

    cout << "\n---------------------------------------------------\n";


    //TIME TO SOLVE / FIND UNSAT
    auto start = chrono::high_resolution_clock::now();
    

    // bool ans = solve(CNF_expr, map, DEBUG_FLAG); // DPLL
    bool ans = solve2WL(CNF_expr, map, wList, trail, decisionLevel, DEBUG_FLAG); //2WL
    if(!ans) cout << "UNSAT\n";

    auto finish = chrono::high_resolution_clock::now();

    chrono::duration<double> elapsed = finish - start;
    cout << "\nTime to solve: " << elapsed.count() << " seconds" << endl;

    return 0;
}