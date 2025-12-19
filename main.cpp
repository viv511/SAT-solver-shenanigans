#include <iostream>
#include <chrono>
#include "solver.h"
#include <sstream>
#include <fstream>
using namespace std;

int numVars = 250;
int numClauses = 0;
expression parseCNF(string filename) {
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

            continue;
        }

        int lit;
        while (ss >> lit) {
            if (lit == 0) {
                if (!c.empty()) {
                    F.push_back(c);
                    c.clear();
                }
            } else {
                c.push_back(lit);
            }
        }
    }

    //redundant check just in case no trailing 0
    if (!c.empty()) {
        F.push_back(c);
    }

    return F;
}

const bool DEBUG_FLAG = false;

int main() {
    expression input = parseCNF("benchmarks/uf250-01.cnf");
    vector<Assignment> map = initialize(numVars);

    //EXPRESSION TO SOLVE:
    cout << "SOLVING THE EXPRESSION: ";
    printExpression(input);


    cout << "\n---------------------------------------------------\n";


    //TIME TO SOLVE / FIND UNSAT
    auto start = chrono::high_resolution_clock::now();
    
    bool ans = solve(input, map, DEBUG_FLAG);
    if(!ans) cout << "UNSAT\n";

    auto finish = chrono::high_resolution_clock::now();
    chrono::duration<double> elapsed = finish - start;
    cout << "\nTime to solve: " << elapsed.count() << " seconds" << endl;


    return 0;
}