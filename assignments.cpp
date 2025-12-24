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