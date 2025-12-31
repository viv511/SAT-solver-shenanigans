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
        expression F;
        std::vector<Assignment> M;
        std::vector<std::vector<int>> watchlist;
        std::vector<int> trail;
        std::vector<int> decisionLevel;
        bool DEBUG;
        int NUM_VARS;
        int NUM_CLAUSES;

        //Initialization functions
        void init();
        std::vector<std::vector<int>> initializeWatchlist(int nV);

        //Helper functions
        bool propagate(int falsifiedLiteral);
        int findUnassigned();
        void assign(int l);
        void undo(size_t targetSize);

        //Core solver function
        bool solve2WL();
};

//Misc functions
bool verifyAssignment(expression& formula, vector<Assignment>& assignments);
bool isTrue(literal l, vector<Assignment>& assignments);
bool isFalse(literal l, vector<Assignment>& assignments);
bool isUnassigned(literal l, vector<Assignment>& assignments);