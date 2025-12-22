#include "2WL_solver.h"
#include "expression.h"
#include <queue>

int findUnassigned(vector<Assignment>& M, expression& F) {
    for(auto& wc : F) {
        bool clauseSatisfied = false;
        
        for(auto lit : wc.C) {
            if(isTrue(lit, M)) {
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

void assign(int l, vector<Assignment>& M, literalTrail& trail) {
    int v = abs(l);
    Assignment a = (l > 0) ? Assignment::TRUE : Assignment::FALSE;

    if(M[v] != Assignment::UNASSIGNED && M[v] != a) {
        cout << "CONFLICTING ASSIGNMENT FOR VARIABLE " << v << " AS " << ((a == Assignment::TRUE) ? "TRUE" : "FALSE") << endl;
        error("ASSIGN ERROR: Conflicting assignment for " + to_string(v));       
    }

    if(M[v] == Assignment::UNASSIGNED) {
        M[v] = a;
        trail.push_back(l); //make sure we are book keeping !!!
    }
}

void undo(vector<Assignment>& M, literalTrail& trail, int target) {
    assert(target >= 0 && target <= trail.size());

    while(trail.size() != target) {
        int l = trail.back();

        //remove the assignments we've given
        M[abs(l)] = Assignment::UNASSIGNED;

        trail.pop_back();
    }
}
bool propogate(int falsifiedLiteral, vector<Assignment>& M, vector<vector<int>>& wList, literalTrail& trail, expression& F) {
    queue<literal> propQueue;
    propQueue.push(falsifiedLiteral);

    while(!propQueue.empty()) {
        literal currentFalsified = propQueue.front();
        propQueue.pop();

        int desiredIndex = litToIndex(currentFalsified);

        size_t i = 0;
        while(i < wList[desiredIndex].size()) {
            int clauseIndexInExpr = wList[desiredIndex][i];
            watchedClause& wc = F[clauseIndexInExpr];

            literal otherWC = wc.getOtherWatch(currentFalsified);

            //Case 1 --- Already good
            if(isTrue(otherWC, M)) {
                i++;
                continue;
            }

            //Case 2 --- Find new watch
            bool foundNewWatch = false;
            for(size_t j = 0; j < wc.size(); j++) {
            if(j == wc.w1Index || j == wc.w2Index) continue; //skip w1 and w2

                literal possibleNewWatch = wc.C[j];

                if(!isFalse(possibleNewWatch, M)) {
                    foundNewWatch = true;
            
                    wc.moveWatch(currentFalsified, j);

                //Trick: overwrite current w/ last, then remove last element --> O(1)
                //Order doesn't matter, simply the contents. And speed >>>
                    wList[desiredIndex][i] = wList[desiredIndex].back();
                    wList[desiredIndex].pop_back();

                    int newWCindex = litToIndex(possibleNewWatch);
                    wList[newWCindex].push_back(clauseIndexInExpr);

                    break;
                }
            }

            if(foundNewWatch) {
                continue;
            }

            //Case 3 --- No new watch (either unit or conflict)

            //CONFLICT:
            if(isFalse(otherWC, M)) {
                return false;
            }

            //UNIT:
            assign(otherWC, M, trail);
            propQueue.push(-otherWC);

            i++;
        }
    }

    return true;
}

bool solve2WL(expression& F, vector<Assignment>& M, vector<vector<int>>& wList, literalTrail& trail, vector<int>& decisionLevel, bool DEBUG) {
    queue<literal> initialUnits;

    for(auto wc : F) {
        if(wc.isUnit()) {
            initialUnits.push(wc.getW1()); //either watch works
        }
    }

    while(!initialUnits.empty()) {
        literal L = initialUnits.front();
        initialUnits.pop();
        
        if(M[abs(L)] != Assignment::UNASSIGNED) continue;
        
        assign(L, M, trail);
        if(!propogate(-L, M, wList, trail, F)) {
            return false;
        }
    }

    int v = findUnassigned(M, F);
    
    if(v == 0) {
        //SAT!
        printAssignments(M);
        return true;
    }

    if(DEBUG) {
        cout << "Deciding variable " << v << "\tat level\t" << decisionLevel.size() + 1 << endl;
    }

    //Assign v = TRUE
    decisionLevel.push_back(trail.size()); //store current level size
    assign(v, M, trail); //assign v as true

    if(propogate(-v, M, wList, trail, F)) {
        if(solve2WL(F, M, wList, trail, decisionLevel, DEBUG)) {
            return true;
        }
    }

    undo(M, trail, decisionLevel.back()); //undo to previous state
    decisionLevel.pop_back(); //go back to prev level size

    //Assign v = FALSE
    decisionLevel.push_back(trail.size()); //store current level size
    assign(-v, M, trail); //assign v as false

    if(propogate(v, M, wList, trail, F)) {
        if(solve2WL(F, M, wList, trail, decisionLevel, DEBUG)) {
            return true;
        }
    }

    undo(M, trail, decisionLevel.back()); //undo to previous state
    decisionLevel.pop_back(); //go back to prev level size

    return false;
}