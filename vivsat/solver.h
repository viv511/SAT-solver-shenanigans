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
        size_t qhead = 0; //Index of next literal to propagate (instead of wasting queue space, keep a size_t idx)
        std::vector<int> trailBounds; //Stores indices in trail where each decision level starts
        
        bool DEBUG;
        int NUM_VARS;
        int NUM_CLAUSES;

        //Initialization functions
        void init();
        std::vector<std::vector<int>> initializeWatchlist(int nV);

        //Helper functions
        int propagate();
        int findUnassigned();
        void assign(int l);
        void undo(size_t targetSize);

        //Core solver function
        bool solve2WL();
        bool solveCDCL(); //todo
};

//Misc functions
bool verifyAssignment(expression& formula, vector<Assignment>& assignments);
bool isTrue(literal l, vector<Assignment>& assignments);
bool isFalse(literal l, vector<Assignment>& assignments);
bool isUnassigned(literal l, vector<Assignment>& assignments);