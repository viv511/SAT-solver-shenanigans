#include "solver.h"

// == CONSTRUCTOR == //
Solver::Solver(bool debugFlag) {
    this->DEBUG = debugFlag;
}

// == CNF/DIMACS PARSING == //
void Solver::readCNF(string filename) {
    expression tmpF;
    clause tmpC;

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
            ss >> p >> cnf >> this->NUM_VARS >> this->NUM_CLAUSES;

            if(p != "p" || cnf != "cnf" || this->NUM_VARS < 1 || this->NUM_CLAUSES < 1) {
                error("Invalid p-line");
            }

            tmpF.reserve(this->NUM_CLAUSES);
            continue;
        }

        int lit;
        
        while (ss >> lit) {
            if (lit == 0) {
                if (!tmpC.empty()) {
                    tmpF.push_back(watchedClause(tmpC));
                    tmpC.clear();
                }
            } else {
                tmpC.push_back(lit);
            }
        }
    }

    //Redundant check for trailing 0
    if(!tmpC.empty()) {
        tmpF.push_back(watchedClause(tmpC));
    }

    //ERROR CHECKS
    if(tmpF.size() != this->NUM_CLAUSES) {
        error("Clause count mismatch!\nExpected " +
          to_string(this->NUM_CLAUSES) + ", got " +
          to_string(tmpF.size()));
    }
    if(tmpF.empty()) error("Empty expression found");
    if(!foundPLine) error("No p-line found");

    this->F = tmpF;

    init();
}

// == MAIN SOLVER == //
bool Solver::solve() {
    cout << "\nSolving an expression with " << NUM_VARS << " variables and " << NUM_CLAUSES << " clauses:\n";

    if(this->DEBUG) {
        printExpression(this->F);
    }

    expression copy = this->F; //copy for later verification

    auto start = chrono::high_resolution_clock::now();
    // bool result = solve2WL();
    bool result = solveCDCL();
    auto finish = chrono::high_resolution_clock::now();

    chrono::duration<double> elapsed = finish - start;
    cout << "\nTime to solve: " << elapsed.count() << " seconds" << endl;

    bool verified = verifyAssignment(copy, this->M);
    
    if(!result) cout << "UNSAT\n";
    else {
        if(!verified) {
            cout << "\nERROR: Assignment does not satisfy expression!\n";
            error("ASSIGNMENT VERIFICATION FAILED!!!");
        }
        else{
            cout << "\nVerified: Assignment satisfies expression.\n\n";
        }
    }

    return result;
}

// == INITIALIZATION FUNCTIONS == //
void Solver::init() {
    M = initializeAssignment(NUM_VARS);
    watchlist = initializeWatchlist(NUM_VARS);
    level.assign(NUM_VARS + 1, -1);
    reason.assign(NUM_VARS + 1, -1);
    trail.clear();
    trailBounds.clear();
    trailBounds.push_back(0);
    qhead = 0;
}

std::vector<std::vector<int>> Solver::initializeWatchlist(int nV) {
    std::vector<std::vector<int>> WL(2 * nV);

    for(size_t i = 0; i < this->F.size(); i++) {
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

// == HELPER FUNCTIONS == //

int Solver::propagate() {
    while(qhead < trail.size()) {
        literal currentFalsified = -trail[qhead++];

        int desiredIndex = litToIndex(currentFalsified);

        size_t i = 0;
        while(i < this->watchlist[desiredIndex].size()) {
            int clauseIndexInExpr = this->watchlist[desiredIndex][i];
            watchedClause& wc = this->F[clauseIndexInExpr];

            literal otherWC = wc.getOtherWatch(currentFalsified);

            //Case 1 --- Already good
            if(isTrue(otherWC, this->M)) {
                i++;
                continue;
            }

            //Case 2 --- Find new watch
            bool foundNewWatch = false;
            for(size_t j = 0; j < wc.size(); j++) {
            if(j == wc.w1Index || j == wc.w2Index) continue; //skip w1 and w2

                literal possibleNewWatch = wc.C[j];

                if(!isFalse(possibleNewWatch, this->M)) {
                    foundNewWatch = true;
            
                    wc.moveWatch(currentFalsified, j);

                    //Trick: overwrite current w/ last, then remove last element --> O(1)
                    //Order doesn't matter, simply the contents. And speed >>>
                    this->watchlist[desiredIndex][i] = this->watchlist[desiredIndex].back();
                    this->watchlist[desiredIndex].pop_back();

                    int newWCindex = litToIndex(possibleNewWatch);
                    this->watchlist[newWCindex].push_back(clauseIndexInExpr);
                    break;
                }
            }

            if(foundNewWatch) {
                continue;
            }

            //Case 3 --- No new watch (either unit or conflict)

            //CONFLICT:
            if(isFalse(otherWC, this->M)) {
                return clauseIndexInExpr;
            }

            //UNIT:
            assign(otherWC, clauseIndexInExpr);
            i++;
        }
    }

    return -1;
}

int Solver::findUnassigned() {
    for(auto& wc : this->F) {
        bool clauseSatisfied = false;
        
        for(auto lit : wc.C) {
            if(isTrue(lit, this->M)) {
                clauseSatisfied = true;
                break;
            }
        }
        
        if(clauseSatisfied) continue;
        
        for(auto lit : wc.C) {
            if(M[abs(lit)] == Assignment::UNASSIGNED) {
                return abs(lit);
            }
        }
    }

    return 0;
}

void Solver::assign(int l, int reasonClause) {
    int v = abs(l);
    Assignment a = (l > 0) ? Assignment::TRUE : Assignment::FALSE;

    if(this->M[v] != Assignment::UNASSIGNED && this->M[v] != a) {
        cout << "CONFLICTING ASSIGNMENT FOR VARIABLE " << v << " AS " << ((a == Assignment::TRUE) ? "TRUE" : "FALSE") << endl;
        error("ASSIGN ERROR: Conflicting assignment for " + to_string(v));       
    }

    if(this->M[v] == Assignment::UNASSIGNED) {
        this->M[v] = a;
        this->level[v] = (int)trailBounds.size() - 1;
        this->reason[v] = reasonClause;
        this->trail.push_back(l);
    }
}

void Solver::undo(size_t target) {
    // assert(target <= this->trail.size());

    while(this->trail.size() != target) {
        int l = this->trail.back();

        //remove the assignments we've given
        this->M[abs(l)] = Assignment::UNASSIGNED;
        this->level[abs(l)] = -1;
        this->reason[abs(l)] = -1;
        this->trail.pop_back();
    }

    // reset qhead if it is beyond the trail size after an undo
    if(qhead > this->trail.size()) qhead = this->trail.size();
}

int Solver::analyze(int conflictClauseIndex, clause& learned) {
    learned.clear();
    learned.push_back(0);

    int counter = 0;
    literal p = 0;

    int i = (int)(this->trail.size()) - 1;
    int c = conflictClauseIndex;

    do {
        watchedClause& wc = this->F[c];

        for(size_t j = 0; j < wc.size(); j++) {
            literal q = wc.C[j];
            int v = abs(q);

            if(q == p || seen[v] || level[v] == 0) continue;

            seen[v] = 1;

            if(level[v] == getDL()) {
                counter++;
            } else {
                learned.push_back(q);
            }
        }

        while(!seen[abs(this->trail[i])]) {
            i--;
        }

        p = this->trail[i];
        c = reason[abs(p)];
        seen[abs(p)] = 0;
        counter--;
    } while(counter > 0);

    // use first UIP technique
    learned[0] = -p;

    // clear other seen flags
    for(size_t j = 0; j < learned.size(); j++) {
        seen[abs(learned[j])] = 0;
    }

    if(learned.size() == 1) return 0;
    
    size_t maxLevel = 1;
    for(size_t j = 1; j < learned.size(); j++) {
        if(level[abs(learned[j])] > level[abs(learned[maxLevel])]) {
            maxLevel = j;
        }
    }
    std::swap(learned[1], learned[maxLevel]);

    return level[abs(learned[1])];
}

bool Solver::solve2WL() {
    queue<literal> initialUnits;

    for(auto& wc : this->F) {
        if(wc.isUnit()) {
            initialUnits.push(wc.getW1()); //either watch works
        }
    }

    while(!initialUnits.empty()) {
        literal L = initialUnits.front();
        initialUnits.pop();
        
        if(isFalse(L, M)) return false;
        if(isTrue(L, M)) continue;
        
        assign(L);
        if(propagate() != -1) {
            return false;
        }
    }

    int v = findUnassigned();
    
    if(v == 0) {
        cout << "SAT" << endl;
        if (this->DEBUG) printAssignments(this->M);
        return true;
    }

    //Assign v = TRUE
    this->trailBounds.push_back(this->trail.size()); //store current level size
    assign(v); //assign v as true

    if(propagate() == -1) {
        if(solve2WL()) {
            return true;
        }
    }

    undo(this->trailBounds.back()); //undo to previous state
    this->trailBounds.pop_back(); //go back to prev level size

    //Assign v = FALSE
    this->trailBounds.push_back(this->trail.size()); //store current level size
    assign(-v); //assign v as false

    if(propagate() == -1) {
        if(solve2WL()) {
            return true;
        }
    }

    undo(this->trailBounds.back()); //undo to previous state
    this->trailBounds.pop_back(); //go back to prev level size
    
    return false;
}

bool Solver::solveCDCL() {
    seen.assign(NUM_VARS + 1, 0);

    for(auto& wc : F) {
        if(!wc.isUnit()) continue;
        literal L = wc.getW1();
        if(isFalse(L, M)) return false;
        if(isUnassigned(L, M)) assign(L);
    }

    while(true) {
        int confl = propagate();

        if(confl != -1) {
            if(getDL() == 0) return false;

            clause learned;
            int bjLevel = analyze(confl, learned);

            undo(trailBounds[bjLevel + 1]);
            trailBounds.resize(bjLevel + 1);

            if(learned.size() == 1) {
                assign(learned[0]);
            } else {
                int idx = F.size();
                F.push_back(watchedClause(learned));
                watchlist[litToIndex(learned[0])].push_back(idx);
                watchlist[litToIndex(learned[1])].push_back(idx);
                assign(learned[0], idx);
            }
        } else {
            int v = findUnassigned();
            if(v == 0) { cout << "SAT" << endl; if(DEBUG) printAssignments(M); return true; }
            trailBounds.push_back(trail.size());
            assign(v);
        }
    }
}

// == MISC FUNCTIONS == //
bool verifyAssignment(expression& formula, vector<Assignment>& assignments) {
    for(size_t i = 0; i < formula.size(); i++) {
        watchedClause& wc = formula[i];
        bool clauseSatisfied = false;
        for(literal l : wc.C) {
            if(isTrue(l, assignments)) {
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
                cout << "v" << v << "=" << (assignments[v] == Assignment::TRUE ? "T" : (assignments[v] == Assignment::FALSE ? "F" : "U")) << " ";
            }
            cout << "\n";
            return false;
        }
    }
    return true;
}

bool isTrue(literal l, vector<Assignment>& assignments) {
    int v = abs(l);
    if(l > 0) {
        return assignments[v] == Assignment::TRUE;
    } else {
        return assignments[v] == Assignment::FALSE;
    }
}

bool isFalse(literal l, vector<Assignment>& assignments) {
    return isTrue(-l, assignments);
}

bool isUnassigned(literal l, vector<Assignment>& assignments) {
    int v = abs(l);
    return assignments[v] == Assignment::UNASSIGNED;
}