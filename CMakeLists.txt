cmake_minimum_required(VERSION 3.24)
project(multilinear_sat LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
if(NOT CMAKE_BUILD_TYPE)
    set(CMAKE_BUILD_TYPE Release)
endif()

option(MULTILINEAR_SAT_CUDA "Build the CUDA backend if a CUDA compiler is found" ON)
option(MULTILINEAR_SAT_TESTS "Build the unit tests" ${PROJECT_IS_TOP_LEVEL})
option(MULTILINEAR_SAT_CLI "Build the command line" ${PROJECT_IS_TOP_LEVEL})

include(CheckLanguage)
set(MULTILINEAR_SAT_HAVE_CUDA OFF)
if(MULTILINEAR_SAT_CUDA)
    check_language(CUDA)
    if(CMAKE_CUDA_COMPILER)
        if(NOT CMAKE_CUDA_ARCHITECTURES)
            set(CMAKE_CUDA_ARCHITECTURES native)   # must precede enable_language, which otherwise defaults to 52
        endif()
        enable_language(CUDA)
        set(CMAKE_CUDA_STANDARD 20)
        set(MULTILINEAR_SAT_HAVE_CUDA ON)
    else()
        message(STATUS "No CUDA compiler found: building the CPU backend only")
    endif()
endif()

find_package(OpenMP)

if(MULTILINEAR_SAT_HAVE_CUDA)
    set(MULTILINEAR_SAT_DEVICE_SOURCES solver/cuda_backend.cu solver/cuda_walk.cu solver/cuda_tilted.cu)
else()
    set(MULTILINEAR_SAT_DEVICE_SOURCES solver/cuda_unavailable.cpp)
endif()

add_library(multilinear_sat STATIC
    solver/formula.cpp
    solver/cpu_backend.cpp
    solver/cpu_walk.cpp
    solver/cpu_tilted.cpp
    solver/solver.cpp
    ${MULTILINEAR_SAT_DEVICE_SOURCES})
target_include_directories(multilinear_sat PUBLIC ${CMAKE_CURRENT_SOURCE_DIR}/solver)
target_compile_options(multilinear_sat PRIVATE $<$<COMPILE_LANGUAGE:CXX>:-Wall -Wextra -O3>)
if(OpenMP_CXX_FOUND)
    target_link_libraries(multilinear_sat PUBLIC OpenMP::OpenMP_CXX)
endif()
if(MULTILINEAR_SAT_HAVE_CUDA)
    target_compile_definitions(multilinear_sat PUBLIC MULTILINEAR_SAT_HAVE_CUDA=1)
    set_target_properties(multilinear_sat PROPERTIES CUDA_SEPARABLE_COMPILATION OFF)
endif()

if(MULTILINEAR_SAT_CLI)
    add_executable(multilinear-sat cli/main.cpp)
    target_link_libraries(multilinear-sat PRIVATE multilinear_sat)
endif()

if(MULTILINEAR_SAT_TESTS)
    enable_testing()
    add_executable(unit_tests
        tests/main.cpp tests/test_formula.cpp tests/test_energy.cpp tests/test_random_and_luby.cpp
        tests/test_solver.cpp tests/test_backends.cpp tests/test_certificate.cpp
        tests/test_walk.cpp tests/test_parity.cpp tests/test_posterior.cpp tests/test_tilted.cpp)
    target_include_directories(unit_tests PRIVATE ${CMAKE_CURRENT_SOURCE_DIR}/tests)
    target_link_libraries(unit_tests PRIVATE multilinear_sat)
    add_test(NAME unit_tests COMMAND unit_tests)
endif()
