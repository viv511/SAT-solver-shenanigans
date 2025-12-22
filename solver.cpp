#include "assignments.h"
#include "expression.h"
#include "solver.h"
#include <utility>

expression simplify(expression F, int L) {
    expression newF;
    newF.reserve(F.size());

    //Clauses can never grow, so we can reserve space
    for(const watchedClause& wc : F) {
        clause C = wc.C;
        // 1) Remove satisfied clauses
        if(find(C.begin(), C.end(), L) != C.end()) continue;

        clause newC;
        newC.reserve(C.size());

        // 2) Remove negated literal
        for(const int& l : C) {
            if (l != -L) newC.push_back(l);
        }

        newF.push_back(std::move(newC));
    }

    return newF;
}


bool solve(expression F, vector<Assignment>& M, const bool DEBUG_FLAG) {
    //TODO in-place undo tracking

    //Unit Propagation, return false if UNSAT
    if(!unitPropagate(F, M, DEBUG_FLAG)) {
        return false;
    }
    
    //UNSAT!
    if(hasEmptyClause(F)) {
        return false;
    }

    //SATISFIABLE!
    //TODO: Change to add current SAT as negated to ALLSAT
    if(F.empty()) {
        printAssignments(M);
        return true;
    }

    //Look for first unassigned literal
    int v = 0;
    for(const watchedClause& wc : F) {
        for(const int& l : wc.C) {
            if(M[abs(l)] == Assignment::UNASSIGNED){
                v = abs(l);
                break;
            }
        }
        if(v != 0) break; //keep searching until found
    }

    if(v == 0) {
        //All variables have been assigned --> SAT
        printAssignments(M);
        return true;
    }

    //branch var = true and var = false
    if(DEBUG_FLAG) {
        cout << "Branching on variable: " << v << endl;
    }

    expression F1 = simplify(F, v);
    vector<Assignment> M1 = M;
    M1[v] = Assignment::TRUE;

    expression F2 = simplify(F, -v);
    vector<Assignment> M2 = M;
    M2[v] = Assignment::FALSE;

    if(solve(F1, M1, DEBUG_FLAG)) return true;
    if(solve(F2, M2, DEBUG_FLAG)) return true;

    return false;
}

bool unitPropagate(expression& F, vector<Assignment>& M, const bool DEBUG_FLAG) {
    if(DEBUG_FLAG) {
        cout << "Unit propagation on: ";
        printExpression(F);
        cout << endl;
    }

    bool propogating = true;

    while(propogating) {
        propogating = false;

        for(const watchedClause& wc : F) {
            //UNSAT condition: empty clause exists
            if(wc.empty()) return false;

            if(wc.size() == 1) {
                if(DEBUG_FLAG) {
                    cout << "Unit clause found: ";
                    printClause(wc.C);
                    cout << endl;
                }

                //Propagate L
                int L = wc.C[0];
                int v = abs(L);
                Assignment desired = (L > 0) ? Assignment::TRUE
                                             : Assignment::FALSE;

                //If assignment already exists, must match existing assignment
                if(M[v] != Assignment::UNASSIGNED && M[v] != desired) {
                    return false;
                }

                if(M[v] == Assignment::UNASSIGNED) {
                    //If L, assign true, if !L assign false
                    M[v] = desired;
                    F = simplify(F, L);
                    propogating = true;
                    break;
                }   
            }
        }
    }

    return true;
}
