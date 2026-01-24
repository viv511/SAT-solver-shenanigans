#include "solver.h"

using namespace std;

const bool DEBUG_FLAG = true;

void runEasyTests(Solver sol) {
    vector<string> testFiles = {
        // "tests/benchmarks/uf20-01.cnf",
        "tests/benchmarks/uf20-010.cnf",
        // "tests/benchmarks/uf20-0100.cnf",
        // "tests/benchmarks/uf20-01000.cnf",
        // "tests/benchmarks/uf20-067.cnf",
    };

    for(string filename : testFiles) {
        sol.readCNF(filename);
        sol.solve();
    }
}

void runHardTests(Solver sol) {
    vector<string> testFiles = {
        // "tests/benchmarks/uf250-01.cnf", //0.5s
        // "tests/benchmarks/uf250-02.cnf",
        // "tests/benchmarks/uf250-03.cnf",
        // "tests/benchmarks/uf250-04.cnf",
        // "tests/benchmarks/uf250-05.cnf",
    };

    for(string filename : testFiles) {
        sol.readCNF(filename);
        sol.solve();
    }
}

void runSudokuTest(Solver sol) {
    sol.readCNF("tests/sudoku.cnf");
    sol.solve();
}

int main() {
    // expression CNF_expr = parseCNF("benchmarks/uf20-0100.cnf");
    // expression CNF_expr = parseCNF("benchmarks/uf250-01.cnf");

    Solver solver(DEBUG_FLAG);

    // solver.readCNF("cdcl.cnf");
    // solver.solve();

    runEasyTests(solver);
    // runHardTests(solver);
    // runSudokuTest(solver);

    return 0;
}