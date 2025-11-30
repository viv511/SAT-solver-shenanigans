#include "expression.h"
#include "solver.h"
#include <utility>
using namespace std;

void printAssignments(unordered_map<int,bool>& M) {
    cout << "SATISFIABLE with assignments: " << endl;
    for(auto a: M) {
        cout << a.first << " -> " << (a.second ? "TRUE" : "FALSE") << endl;
    }
}

expression simplify(expression F, int L) {
    expression newF;
    newF.reserve(F.size());

    //Clauses can never grow, so we can reserve space
    for (clause C : F) {
        // 1) Remove satisfied clauses
        if (find(C.begin(), C.end(), L) != C.end()) continue;

        clause newC;
        newC.reserve(C.size());

        // 2) Remove negated literal
        for (int l : C) {
            if (l != -L) newC.push_back(l);
        }

        newF.push_back(std::move(newC));
    }

    return newF;
}


bool solve(expression F, unordered_map<int,bool>& M, const bool DEBUG_FLAG) {
    //TODO in-place undo tracking

    //Unit Propagation, return false if UNSAT
    if(!unitPropagate(F, M, DEBUG_FLAG)) return false;

    //UNSAT!
    if(hasEmptyClause(F)) return false;
    
    //SATISFIABLE!
    //TODO: Change to add current SAT as negated to ALLSAT
    if(F.empty()) {
        printAssignments(M);
        return true;
    }

    //Look for first unassigned literal
    int v = 0;
    for(clause C : F) {
        for(int l : C) {
            if(M.count(absIndex(l)) == 0){
                v = absIndex(l);
                break;
            }
        }
        if(v != 0) break; //keep searching until found
    }

    if(v == 0) {
        //All variables assigned but expression not empty or unsat?
        //Should be unreachable
        cout << "ERROR: unreachable! all assigned but expression not empty or unsat??" << endl;
        return false;
    }

    //branch var = true and var = false
    if(DEBUG_FLAG) {
        cout << "Branching on variable: " << v << endl;
    }

    expression F1 = simplify(F, v);
    expression F2 = simplify(F, -v);
    unordered_map<int,bool> M1 = M;
    M1[v] = true;
    unordered_map<int,bool> M2 = M;
    M2[v] = false;

    if(solve(F1, M1, DEBUG_FLAG)) return true;
    if(solve(F2, M2, DEBUG_FLAG)) return true;

    return false;
}

bool unitPropagate(expression& F, unordered_map<int,bool>& M, const bool DEBUG_FLAG) {
    if(DEBUG_FLAG) {
        cout << "Unit propagation on: ";
        printExpression(F);
        cout << endl;
    }

    bool propogating = true;

    while(propogating) {
        propogating = false;

        for(clause C : F) {
            //UNSAT condition: empty clause exists
            if(C.empty()) return false;

            if(C.size() == 1) {
                if(DEBUG_FLAG) {
                    cout << "Unit clause found: ";
                    printClause(C);
                    cout << endl;
                }

                //Propagate L
                int L = C[0];

                //We know L must evaluate to true
                //Check if it doesnt conflict with existing assignments
                int v = absIndex(L);
                if(M.count(v) && M[v] != (L > 0)) {
                    return false;
                }

                //If L, assign true, if !L assign false
                M[v] = (L > 0);
                F = simplify(F, L);
                propogating = true;
                break;
            }
        }
    }

    return true;
}
