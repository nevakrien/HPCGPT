#!/bin/bash

# Enable 'set -e' to exit the script if any command fails
set -e

mkdir results/combo 
mv perf.data results/combo 
mv code_perf_output.txt results/combo 

cd results/combo
perf script >> output.txt