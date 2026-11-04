#include "solver.h"
#include <filesystem>

using namespace std;
namespace fs = std::filesystem;

const string TEST_DIR = "tests/benchmarks/";
const bool DEBUG_FLAG = false;
vector<string> testFiles;

void testSpecificFile(Solver& s, string filename) {
    s.readCNF(filename);
    s.solve();
}

void runTests(int ufNum) {
    testFiles.clear();
    string prefix = "uf" + to_string(ufNum) + "-";

    if (fs::exists(TEST_DIR) && fs::is_directory(TEST_DIR))  {
        for (const auto& e : fs::directory_iterator(TEST_DIR)) {
            if (e.is_regular_file() && e.path().extension() == ".cnf"
                && e.path().filename().string().rfind(prefix, 0) == 0) {
                testFiles.push_back(e.path().string());
            }
        }
    }

    sort(testFiles.begin(), testFiles.end());

    if (testFiles.empty()) {
        cout << "No benchmark files found for " << prefix << " in " << TEST_DIR << endl;
        return;
    }

    // run all tests
    Solver solver(DEBUG_FLAG);
    for (const string& file : testFiles) {
        cout << "\n=== " << file << " ===";
        try {
            testSpecificFile(solver, file);
        } catch (const exception& ex) {
            cout << "FAILED on " << file << ": " << ex.what() << endl;
        }
    }
}

int main() {
    Solver solver(DEBUG_FLAG);

    // must be either 20, 75, 175, or 250
    runTests(75);
    // testSpecificFile(solver, "tests/sudoku.cnf");

    return 0;
}