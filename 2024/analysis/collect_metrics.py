import json
import statistics
import subprocess
import time

# Paths to directories
PYTHON_DIR = "./python"
RUST_DIR = "./rust"
INPUT_DIR = "./inputs"
RESULTS_FILE = "./results.json"


# Helper function to count lines of code
def count_lines_of_code(file_path):
    with open(file_path) as f:
        lines = f.readlines()
    # Exclude empty lines and comments
    return len([line for line in lines if line.strip() and not line.strip().startswith("#")])


# Run Python solution
def time_python_solution(day, input_file, iterations=10):
    script_path = f"{PYTHON_DIR}/{day}.py"
    times = []
    for _ in range(iterations):
        start_time = time.perf_counter()
        subprocess.run(["python", script_path], check=True)
        end_time = time.perf_counter()
        times.append(end_time - start_time)
    return statistics.mean(times), statistics.stdev(times), count_lines_of_code(script_path)


# Run Rust solution
def time_rust_solution(day, iterations=10):
    # Build Rust project
    subprocess.run(["cargo", "build", "--release"], cwd=RUST_DIR, check=True)

    binary_path = f"{RUST_DIR}/target/release/rust"
    times = []
    for _ in range(iterations):
        start_time = time.perf_counter()
        subprocess.run([binary_path, day], check=True)
        end_time = time.perf_counter()
        times.append(end_time - start_time)

    # Count LOC for Rust implementation
    rust_src_files = [f"{RUST_DIR}/src/{day}.rs"]
    total_loc = sum(count_lines_of_code(file) for file in rust_src_files)

    return statistics.mean(times), statistics.stdev(times), total_loc


if __name__ == "__main__":
    days = ["day01"]  # Add more days as you go
    results = {}

    for day in days:
        input_file = f"{INPUT_DIR}/{day}.txt"

        print(f"Timing Python solution for {day}...")
        python_avg, python_stdev, python_loc = time_python_solution(day, input_file)

        print(f"Timing Rust solution for {day}...")
        rust_avg, rust_stdev, rust_loc = time_rust_solution(day)

        results[day] = {
            "python": {"avg_time": python_avg, "stdev_time": python_stdev, "loc": python_loc},
            "rust": {"avg_time": rust_avg, "stdev_time": rust_stdev, "loc": rust_loc},
        }

    # Save results to JSON
    with open(RESULTS_FILE, "w") as f:
        json.dump(results, f, indent=4)

    print(f"Results saved to {RESULTS_FILE}")
