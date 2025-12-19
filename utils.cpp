#include "utils.h"

void error(const string& message) {
    throw std::runtime_error(message);
}