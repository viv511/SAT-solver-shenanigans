#include "assignments.h"

vector<Assignment> initializeAssignment(int numVars) {
    vector<Assignment> assignments;

    //0 doesnt matter --> we will never access it
    //size is numVars + 1
    for(int i = 0; i < numVars + 1; i++) {
        assignments.push_back(Assignment::UNASSIGNED);
    }

    return assignments;
}

void printAssignments(vector<Assignment>& M) {
    cout << "\n---------------------------------------------------\n";
    cout << "v ";
    for(int i = 1; i < M.size(); i++) {
        //We don't care about unassigned variables, as long as SAT
        if(M[i] != Assignment::UNASSIGNED) {
            cout << (M[i] == Assignment::TRUE ? "" : "-") << i << " ";
        }
    }

    cout << "\n---------------------------------------------------\n";
}