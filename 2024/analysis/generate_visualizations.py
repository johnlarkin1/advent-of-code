import json

import matplotlib.pyplot as plt

RESULTS_FILE = "./results.json"


def generate_bar_chart(data, key, title, ylabel, filename):
    days = list(data.keys())
    python_values = [float(data[day]["python"][key].replace("µs", "").replace("ms", "")) for day in days]
    rust_values = [float(data[day]["rust"][key].replace("µs", "").replace("ms", "")) for day in days]

    x = range(len(days))
    plt.figure(figsize=(10, 6))
    plt.bar(x, python_values, width=0.4, label="Python", align="center")
    plt.bar([p + 0.4 for p in x], rust_values, width=0.4, label="Rust", align="center")
    plt.xticks(x, days, rotation=45)
    plt.ylabel(ylabel)
    plt.title(title)
    plt.legend()
    plt.tight_layout()
    plt.savefig(filename)
    plt.close()


def generate_timing_error_chart(data, title, ylabel, filename):
    days = list(data.keys())
    python_avg = [float(data[day]["python"]["avg_time"].replace("µs", "").replace("ms", "")) for day in days]
    python_min = [float(data[day]["python"]["min_time"].replace("µs", "").replace("ms", "")) for day in days]
    python_max = [float(data[day]["python"]["max_time"].replace("µs", "").replace("ms", "")) for day in days]
    rust_avg = [float(data[day]["rust"]["avg_time"].replace("µs", "").replace("ms", "")) for day in days]
    rust_min = [float(data[day]["rust"]["min_time"].replace("µs", "").replace("ms", "")) for day in days]
    rust_max = [float(data[day]["rust"]["max_time"].replace("µs", "").replace("ms", "")) for day in days]

    x = range(len(days))
    plt.figure(figsize=(10, 6))

    # Python error bars
    plt.errorbar(
        x,
        python_avg,
        yerr=[[(a - b) for a, b in zip(python_avg, python_min)], [(a - b) for a, b in zip(python_max, python_avg)]],
        fmt="o",
        label="Python",
        capsize=5,
    )

    # Rust error bars
    plt.errorbar(
        x,
        rust_avg,
        yerr=[[(a - b) for a, b in zip(rust_avg, rust_min)], [(a - b) for a, b in zip(rust_max, rust_avg)]],
        fmt="o",
        label="Rust",
        capsize=5,
    )

    plt.xticks(x, days, rotation=45)
    plt.ylabel(ylabel)
    plt.title(title)
    plt.legend()
    plt.tight_layout()
    plt.savefig(filename)
    plt.close()


if __name__ == "__main__":
    # Load results
    with open(RESULTS_FILE) as f:
        data = json.load(f)

    # Generate bar chart for average execution time
    generate_bar_chart(data, "avg_time", "Average Execution Time", "Time (µs)", "avg_time_comparison.png")

    # # Generate error chart for timing variability
    # generate_timing_error_chart(data, "Timing Variability (Min/Max/Avg)", "Time (µs)", "timing_variability.png")
