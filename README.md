# TinyGPT
Benchmarking of a tiny C++11 GPT-2 inference implementation from scratch, which is mainly based on the project [TinyGPT](https://github.com/keith2018/TinyGPT).
the goal is to learn and show how benchmarking works and how code can be parallelized with openmp. the [original code](https://github.com/keith2018/TinyGPT) while very well made in terms of the build system had some core issues with straight for loops. runing a profiler on it would show fairly poor core utilization.

we will specifcly find the areas of code that need to be optimized and work from there.

## System Requirements

The core of the code is cross-platform, designed to function on various systems. However, for benchmarking purposes, we concentrate on Linux or Unix-based environments. To utilize benchmarking features, you'll require Linux perf tools and a Unix C time ABI.

We also assume the presence of Python and Matplotlib for generating graphs. On Windows, exclude the benchmarking compilation macro when using CMake.

## Core class

- [`Tensor`](src/Tensor.h): Tensor class similar to the [numpy](https://numpy.org/doc/1.25/reference/routines.html) interface.
- [`Model`](src/Model.h): GPT-2 model implementation with reference to [gpt2_pico.py](https://github.com/jaymody/picoGPT/blob/main/gpt2_pico.py).
- [`Tokenizer`](src/Tokenizer.h): BPE tokenizer with exactly the same logic as GPT-2 [encoder.py](https://github.com/openai/gpt-2/blob/master/src/encoder.py).
- [`class PerfLogger`](src/PerfLogger.h) benchmarking logger with minimal overhead writes to file on destruction

## Build and Run

### 1. Get the code

```bash
git clone --recurse-submodules https://github.com/nevakrien/HPCGPT.git
```

### 2. Install Intel MKL(Math Kernel Library)

Official website: [Intel®-Optimized Math Library for Numerical Computing on CPUs & GPUs](https://www.intel.com/content/www/us/en/developer/tools/oneapi/onemkl.html)

### 3. Download GPT-2 model file
    
```python
python3 tools/download_gpt2_model.py
```
if success, you'll see the file `model_file.data` in directory `assets/gpt2`

### 4. Build and Run

infrence cross platform:
```bash
mkdir build
cmake -B ./build -DCMAKE_BUILD_TYPE=RelWithDebInfo 
cmake --build ./build --config Release
```

This will generate the executable file and copy assets to directory `build/bin`, then you can run the demo:

benchmarking unix only
```bash
mkdir build_timer
cmake -B ./build_timer -DCMAKE_BUILD_TYPE=RelWithDebInfo -DNEVA_TIME_BENCHMARK=ON
cmake --build ./build_timer --config Release
```

## Dependencies

- GEMM acceleration
  - `intel-mkl` [https://www.intel.com/content/www/us/en/developer/tools/oneapi/onemkl.html](https://www.intel.com/content/www/us/en/developer/tools/oneapi/onemkl.html)
- Json parser
  - `json11` [https://github.com/dropbox/json11](https://github.com/dropbox/json11)
- Tokenizer regular matching
  - `re2` [https://github.com/google/re2](https://github.com/google/re2)
  - `abseil-cpp` [https://github.com/abseil/abseil-cpp](https://github.com/abseil/abseil-cpp)

## License

This code is licensed under the MIT License (see [LICENSE](LICENSE)).

# self notes

I have looked at both vtune and perf and the code is basicly linear so its really wasting a lot of potential even on an 8 core system it would probably do poorly. 

looking into what I can get out of perf wasnt enogh i did an attempt of this but it seems to just be random parts of code with no structure we need to tell the profiler exacly what part of code we care about 

gona try adding some tooling around this I would do my best to macro it in a way where u can toggle it on or off depending on what u want. maybe I would just make 2 diffrent areas of code but that seems fishy 