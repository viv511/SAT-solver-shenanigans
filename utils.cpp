#include "utils.h"

int NUM_VARS = 0;
int NUM_CLAUSES = 0;

void printAssignments(vector<Assignment>& M) {
    cout << "SAT" << endl;
    cout << "v ";
    for(int i = 1; i < M.size(); i++) {
        //We don't care about unassigned variables, as long as SAT
        if(M[i] != Assignment::UNASSIGNED) {
            cout << (M[i] == Assignment::TRUE ? "" : "-") << i << " ";
        }
        //OPTIONAL: if u need to assign all assignments, just convert the unassigned to all true or all false
    }

    cout << "\n---------------------------------------------------\n";
}

void error(const string& message) {
    throw std::runtime_error(message);
}

int litToIndex(const literal& l) {
    return 2 * (abs(l) - 1) + ((l < 0) ? 1 : 0);
}

bool isTrue(literal l, vector<Assignment>& M) {
    int v = abs(l);
    if(l > 0) {
        return M[v] == Assignment::TRUE;
    } else {
        return M[v] == Assignment::FALSE;
    }
}

bool isFalse(literal l, vector<Assignment>& M) {
    return isTrue(-l, M);
}

bool isUnassigned(literal l, vector<Assignment>& M) {
    int v = abs(l);
    return M[v] == Assignment::UNASSIGNED;
}
