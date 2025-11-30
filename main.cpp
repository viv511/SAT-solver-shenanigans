#include <iostream>
#include <chrono>
#include "expression.h"
#include <unordered_map>
#include "solver.h"
#include <sstream>
#include <fstream>
using namespace std;

expression parseInputFile(string filename) {
    //String: (x ∨ y ∨ ¬z) ∧ (¬y ∨ z) as
    //SAMPLE INPUT "1 2 -3 0 -2 3 0"

    expression F;
    clause c;

    //Read file
    ifstream infile(filename);
    string s;

    while (getline(infile, s)) {
        stringstream ss(s);
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

const bool DEBUG_FLAG = true;

int main() {
    expression input = parseInputFile("tests/unsat_costas4.txt");
    unordered_map<int, bool> map;


    cout << "SOLVING THE EXPRESSION: ";
    printExpression(input);
    cout << "---------------------------------------------------\n";

    auto start = chrono::high_resolution_clock::now();
    if(!solve(input, map, DEBUG_FLAG)) {
        cout << "\nUNSATISFIABLE!" << endl;
    }
    auto finish = chrono::high_resolution_clock::now();
    chrono::duration<double> elapsed = finish - start;
    cout << "Time to solve: " << elapsed.count() << " seconds" << endl;

    return 0;
}