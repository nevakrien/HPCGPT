cmake_minimum_required(VERSION 3.10)
project(TinyGPT)

set(CMAKE_CXX_STANDARD 11)

set(MKL_ARCH intel64)
set(MKL_LINK static)
set(MKL_THREADING intel_thread)
find_package(MKL CONFIG REQUIRED)


# Set the output directory for binaries and libraries
set(CMAKE_RUNTIME_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/bin)
set(CMAKE_LIBRARY_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/lib)
set(CMAKE_ARCHIVE_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/lib)



# Option for NEVA Time Benchmarking, OFF by default
option(NEVA_TIME_BENCHMARK "Enable NEVA Time Benchmarking" OFF)

# Check if NEVA_TIME_BENCHMARK is enabled and act accordingly
if(NEVA_TIME_BENCHMARK)
    add_compile_definitions(NEVA_TIME_BENCHMARK=1)
    message(STATUS "NEVA_TIME_BENCHMARK is enabled.")
else()
    message(STATUS "NEVA_TIME_BENCHMARK is disabled.")
endif()

# Option for using the optimized multiHeadAttention, OFF by default
option(USE_OPTIMIZED_ATTENTION "Use Optimized multiHeadAttention" OFF)

# Check if USE_OPTIMIZED_ATTENTION is enabled and add compile definition
if(USE_OPTIMIZED_ATTENTION)
    add_compile_definitions(USE_OPTIMIZED_ATTENTION=1)
    message(STATUS "USE_OPTIMIZED_ATTENTION is enabled.")
else()
    message(STATUS "USE_OPTIMIZED_ATTENTION is disabled.")
endif()

add_subdirectory(src)
add_subdirectory(app)
add_subdirectory(benchmark)

