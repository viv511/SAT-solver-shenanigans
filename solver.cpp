#include "solver.h"
#include "clause.h"
#include "expression.h"
#include "utils.h"

// == CONSTRUCTOR == //
Solver::Solver(bool debugFlag) {
    this->DEBUG = debugFlag;

    this->NUM_CLAUSES = 0;
    this->NUM_VARS = 0;
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
}

// == MAIN SOLVER == //
bool Solver::solve() {
    // REQUIRES: readCNF has been called
    // ENSURES: returns true if SAT, false if UNSAT
    if(NUM_CLAUSES == 0 && NUM_VARS == 0) {
        error("No CNF read before calling solve()");
    }

    init();

    cout << "\nSolving an expression with " << NUM_VARS << " variables and " << NUM_CLAUSES << " clauses:\n";

    if(this->DEBUG) {
        printExpression(this->F);
    }

    cout << "\n---------------------------------------------------\n";

    expression copy = this->F; //copy for later verification

    auto start = chrono::high_resolution_clock::now();
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

    trail.clear();
    trailBounds.clear();
    trailBounds.push_back(0);

    //+1 since variables are 1-indexed
    decisionLevel = std::vector<int>(NUM_VARS + 1, 0);
    reasoned = std::vector<int>(NUM_VARS + 1, -1);
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

int Solver::propagate(int falsifiedLiteral) {
    std::queue<literal> propQueue;
    propQueue.push(falsifiedLiteral);

    while(!propQueue.empty()) {
        literal currentFalsified = propQueue.front();
        propQueue.pop();

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
            propQueue.push(-otherWC);

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

void Solver::assign(int l, int reasonedValue) {
    int v = abs(l);
    Assignment a = (l > 0) ? Assignment::TRUE : Assignment::FALSE;

    //Sanity check here !!!
    if(this->M[v] != Assignment::UNASSIGNED && this->M[v] != a) {
        cout << "CONFLICTING ASSIGNMENT FOR VARIABLE " << v << " AS " << ((a == Assignment::TRUE) ? "TRUE" : "FALSE") << endl;
        error("ASSIGN ERROR: Conflicting assignment for " + to_string(v));       
    }

    if(this->M[v] == Assignment::UNASSIGNED) {
        this->M[v] = a;

        this->decisionLevel[v] = this->trailBounds.size() - 1;
        this->reasoned[v] = reasonedValue;

        this->trail.push_back(l);
    }
}

void Solver::undo(size_t target) {
    // assert(target <= this->trail.size());

    while(this->trail.size() != target) {
        int l = this->trail.back();

        //remove the assignments we've given
        this->M[abs(l)] = Assignment::UNASSIGNED;
        this->trail.pop_back();
    }
}

std::tuple<clause, int> Solver::analyze(int conflictClauseIndex) {
    clause learnedClause = {};

    int currentDecisionLevel = this->trailBounds.size() - 1;

    std::vector<bool> seen(NUM_VARS + 1, false);
    int numAtCurrentLevel = 0;

    //Start with conflict clause
    watchedClause& conflictClause = this->F[conflictClauseIndex];
    for(literal l : conflictClause.C) {
        int v = abs(l);
        if(v == 0) continue;
        seen[v] = true;

        if(this->decisionLevel[v] == currentDecisionLevel) numAtCurrentLevel++;
        else learnedClause.push_back(l);
    }

    //Resolve (First UIP)
    literal lastAssigned = 0;

    for(int i = this->trail.size() - 1; i >= 0 && numAtCurrentLevel > 1; i--) {
        lastAssigned = trail[i];
        int v = abs(lastAssigned);

        if(!seen[v]) continue;

        int reasonClauseIndex = this->reasoned[v];
        if(reasonClauseIndex == -1) continue;

        watchedClause& reasonClause = this->F[reasonClauseIndex];
        for(literal l : reasonClause.C) {
            int u = abs(l);

            if(u == 0 || seen[u]) continue;
            seen[u] = true;

            if(this->decisionLevel[u] == currentDecisionLevel) numAtCurrentLevel++;
            else learnedClause.push_back(l);
        }

        seen[v] = false;
        numAtCurrentLevel--;
    }

    //Add negation of UIP (only if valid)
    if(lastAssigned != 0) {
        learnedClause.push_back(-lastAssigned);
    }

    //Figure out backjump level
    int backjumpLevel = 0;
    for(literal l : learnedClause) { 
        int v = abs(l);
        if(v > 0 && decisionLevel[v] < currentDecisionLevel) {
            backjumpLevel = std::max(backjumpLevel, decisionLevel[v]);
        }
    }

    return {learnedClause, backjumpLevel};
}

bool Solver::solve2WL() {
    queue<literal> initialUnits;

    for(auto wc : this->F) {
        if(wc.isUnit()) {
            initialUnits.push(wc.getW1()); //either watch works
        }
    }

    while(!initialUnits.empty()) {
        literal L = initialUnits.front();
        initialUnits.pop();
        
        if(this->M[abs(L)] != Assignment::UNASSIGNED) continue;
        
        assign(L, -1);
        if(propagate(-L) != -1) {
            return false;
        }
    }

    int v = findUnassigned();
    
    if(v == 0) {
        //SAT!
        printAssignments(this->M);
        return true;
    }

    if(DEBUG) {
        cout << "Deciding variable " << v << "\tat level " << trailBounds.size() + 1 << endl;
    }

    //Assign v = TRUE
    this->trailBounds.push_back(this->trail.size()); //store current level size
    assign(v, -1); //assign v as true

    if(propagate(-v) == -1) {
        if(solve2WL()) {
            return true;
        }
    }

    undo(this->trailBounds.back()); //undo to previous state
    this->trailBounds.pop_back(); //go back to prev level size

    //Assign v = FALSE
    this->trailBounds.push_back(this->trail.size()); //store current level size
    assign(-v, -1); //assign v as false

    if(propagate(v) == -1) {
        if(solve2WL()) {
            return true;
        }
    }

    undo(this->trailBounds.back()); //undo to previous state
    this->trailBounds.pop_back(); //go back to prev level size
    
    return false;
}

bool Solver::solveCDCL() {
    if(this->DEBUG) {
        cout << "Initial propagation...\n";
    }

    queue<literal> initialUnits;

    for(auto wc : this->F) {
        if(wc.isUnit()) {
            initialUnits.push(wc.getW1()); //either watch works
        }
    }

    while(!initialUnits.empty()) {
        literal L = initialUnits.front();
        initialUnits.pop();
        
        if(this->M[abs(L)] != Assignment::UNASSIGNED) continue;
        
        assign(L, -1);
        if(propagate(-L) != -1) {
            return false;
        }
    }

    int z = 0;
    while(true) {
        if(z == 67) error("forced stop");
        // if(this->DEBUG) {
        //     cout << "\nDecision Level " << trailBounds.size() << " // F.size() = " << this->F.size() << " // Trail Bounds size: " << this->trailBounds.size();
        // }

        int v = findUnassigned();
        if(v == 0) {
            //SAT!
            printAssignments(this->M);
            return true;
        }

        //F := Simplify(F(v = TRUE))
        trailBounds.push_back(trail.size());
        assign(v, -1);

        int C_conflict = propagate(-v);

        while(C_conflict != -1) {
            // C_conflict := Analyze(C_falsified)
            std::tuple<clause,int> analysis = analyze(C_conflict);
            clause C_learned = std::get<0>(analysis);
            int backjumpLevel = std::get<1>(analysis);

            // if(C_conflict == NULL) return UNSAT
            if(trailBounds.size() == 1) {
                //UNSAT
                return false;
            }

            // Backtrack(C_conflict)
            undo(trailBounds[backjumpLevel]);
            trailBounds.resize(backjumpLevel + 1);

            int unassignedCount = 0; 
            for (auto l : C_learned) if (isUnassigned(l, M)) unassignedCount++;

            cout << "Learned clause size=" << C_learned.size()
                << " | unassigned after backjump=" << unassignedCount
                << " | backjumpLevel=" << backjumpLevel << endl;


            // F := Simplify(F U {C_learned})
            if(this->DEBUG) {
                // cout << "\nLearning new clause: ";
                // printClause(C_learned);
                cout << "Conflict Clause index: " << C_conflict << ", backjumping to level " << backjumpLevel << "\n";
                z++;
            }
            this->F.push_back(watchedClause(C_learned));
            
            // Update watchlist
            literal w1 = F.back().getW1();
            literal w2 = F.back().getW2();
            this->watchlist[litToIndex(w1)].push_back(this->F.size() - 1);
            if(w1 != w2) this->watchlist[litToIndex(w2)].push_back(this->F.size() - 1);

            // Propagate 
            literal unitLit = 0;
            for(literal l : C_learned) {
                if(isUnassigned(l, this->M)) {
                    unitLit = l;
                    break;
                }
            }
            
            if(unitLit != 0) {
                // if(this->DEBUG) {
                //     cout << "\nPropagating learned unit literal " << unitLit << " at backjump level " << backjumpLevel << "...\n";
                // }
                
                if(isUnassigned(unitLit, this->M)) {
                    assign(unitLit, this->F.size() - 1);
                    C_conflict = propagate(-unitLit);
                }
                else {
                    C_conflict = -1; //no propagation needed
                }
            } else {
                C_conflict = -1; //no propagation needed
            }
        }
    }
}

// == MISC FUNCTIONS == //
bool verifyAssignment(expression& formula, vector<Assignment>& assignments) {
    for(int i = 0; i < formula.size(); i++) {
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