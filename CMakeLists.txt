cmake_minimum_required(VERSION 3.10)
project(TinyGPT)

set(CMAKE_CXX_STANDARD 11)

set(MKL_ARCH intel64)
set(MKL_LINK static)
set(MKL_THREADING intel_thread)
find_package(MKL CONFIG REQUIRED)

add_subdirectory(src)
add_subdirectory(app)
add_subdirectory(benchmark)

