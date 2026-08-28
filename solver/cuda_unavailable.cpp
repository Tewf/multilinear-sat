// Compiled instead of cuda_backend.cu when the library is built without CUDA.
#include <stdexcept>

#include "backend.hpp"

namespace multilinear_sat {

bool cuda_available() { return false; }

std::unique_ptr<Backend> make_cuda_backend() {
    throw std::runtime_error("this build has no CUDA backend; rebuild with -DMULTILINEAR_SAT_CUDA=ON");
}

}  // namespace multilinear_sat
