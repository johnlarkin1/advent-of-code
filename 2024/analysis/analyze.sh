#!/bin/bash

# For Rust
echo "Measuring Rust solution..."
cd rust
cargo build --release >/dev/null 2>&1 || { echo "Rust build failed"; exit 1; }
rust_times=()
for i in {1..10}; do
    time=$(./target/release/rust day01 | sed -n 's/.*day01: \([0-9.]*\)µs/\1/p')
    rust_times+=("$time")
done
cd ../

# Calculate average time for Rust
rust_avg=$(echo "${rust_times[@]}" | awk '{s=0; for (i=1; i<=NF; i++) s+=$i; print s/NF}')
echo "Rust average time: ${rust_avg}µs"

# For Python
echo "Measuring Python solution..."
python_times=()
for i in {1..10}; do
    time=$(python ./python/day01.py | sed -n 's/.*day01: \([0-9.]*\) µs/\1/p')
    python_times+=("$time")
done

# Calculate average time for Python
python_avg=$(echo "${python_times[@]}" | awk '{s=0; for (i=1; i<=NF; i++) s+=$i; print s/NF}')
echo "Python average time: ${python_avg}µs"
