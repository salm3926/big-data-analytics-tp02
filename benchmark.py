
from pathlib import Path
import csv
import matplotlib.pyplot as plt

# Actual experimental results
methods = [
    "Standard Pandas",
    "Pandas Chunking",
    "Dask DataFrame"
]

execution_times = [120.49, 80.66, 67.22]
peak_memory = [10.86, 0.16, 0.76]

RESULTS_DIR = Path(__file__).resolve().parent / "results"
RESULTS_DIR.mkdir(exist_ok=True)


def create_chart(values, ylabel, title, filename):
    fig, ax = plt.subplots(figsize=(9, 5))

    bars = ax.bar(methods, values)

    ax.set_title(title, fontsize=15, fontweight="bold")
    ax.set_ylabel(ylabel)
    ax.set_ylim(0, max(values) * 1.2)

    ax.bar_label(
        bars,
        fmt="%.2f",
        padding=4
    )

    ax.grid(axis="y", alpha=0.2)
    ax.set_axisbelow(True)

    fig.tight_layout()
    fig.savefig(RESULTS_DIR / filename, dpi=200)
    plt.close(fig)

    print(f"Created: {filename}")


# Execution time chart
create_chart(
    execution_times,
    "Execution Time (seconds)",
    "Execution Time Comparison",
    "execution_time.png"
)

# RAM consumption chart
create_chart(
    peak_memory,
    "Peak RAM (GiB)",
    "Memory Consumption Comparison",
    "memory_usage.png"
)

# Export benchmark data to CSV
with open(
    RESULTS_DIR / "benchmark_results.csv",
    "w",
    newline="",
    encoding="utf-8"
) as file:

    writer = csv.writer(file)

    writer.writerow([
        "Method",
        "Execution_Time_Seconds",
        "Peak_RAM_GiB"
    ])

    for method, execution, ram in zip(
        methods, execution_times, peak_memory
    ):
        writer.writerow([method, execution, ram])

print("\nBenchmark completed successfully!")
