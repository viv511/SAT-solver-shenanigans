#pragma once

#include <iostream>
#include <queue>
#include <sstream>
#include <fstream>
#include <chrono>
#include <iostream>

#include "assignments.h"
#include "expression.h"
#include "utils.h"

class Solver {
    public:
        Solver(bool debugFlag = false);
        void readCNF(string filename);
        bool solve();
        std::vector<Assignment> getAssignments() const { return M; }

    private:
        expression F; //The formula in CNF
        std::vector<Assignment> M; //Current variable assignments
        std::vector<std::vector<int>> watchlist; //Watchlist for 2WL
        std::vector<int> trail; //Stores assigned literals in order
        std::vector<int> trailBounds; //Stores indices in trail where each decision level starts
        std::vector<int> decisionLevel; //Storse the decision level of each v
        std::vector<int> reasoned; //For each v, -1 if decision, else the clause index that implied v

        bool DEBUG;
        int NUM_VARS;
        int NUM_CLAUSES;

        //===== Initialization functions =====//
        void init();
        std::vector<std::vector<int>> initializeWatchlist(int nV);

        //===== Helper functions =====//
        int findUnassigned();

        //CDCL requires return of conflict clause index OR -1 if no conflict
        int propagate(int falsifiedLiteral);

        void assign(int l, int reasonedValue);
        void undo(size_t targetSize);

        std::tuple<clause, int> analyze(int conflictClauseIndex);

        //===== Core solver function =====//
        bool solve2WL();
        bool solveCDCL();
};

//Misc functions
bool verifyAssignment(expression& formula, vector<Assignment>& assignments);
bool isTrue(literal l, vector<Assignment>& assignments);
bool isFalse(literal l, vector<Assignment>& assignments);
bool isUnassigned(literal l, vector<Assignment>& assignments);