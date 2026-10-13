
import os
import time
import threading
from pathlib import Path

import dask
import dask.dataframe as dd
import psutil
from dask.diagnostics import ProgressBar

# Configuration
BASE_DIR = Path(__file__).resolve().parent
DATA_FILE = BASE_DIR / "data" / "train.csv"
RESULTS_DIR = BASE_DIR / "results"

GIB = 1024 ** 3
BLOCK_SIZE = "64MB"

process = psutil.Process(os.getpid())
stop_event = threading.Event()
memory_stats = {"peak": 0}


def monitor_memory():
    while not stop_event.is_set():
        try:
            memory = process.memory_info().rss
            memory_stats["peak"] = max(
                memory_stats["peak"], memory
            )
        except psutil.Error:
            break

        stop_event.wait(0.1)


def main():
    if not DATA_FILE.exists():
        print("Dataset not found!")
        return

    RESULTS_DIR.mkdir(exist_ok=True)

    print("TASK 3: DASK DATAFRAME")
    print(f"Block size: {BLOCK_SIZE}")
    print("Scheduler: Threads")
    print("Workers: 2\n")

    start = time.perf_counter()

    monitor_thread = threading.Thread(
        target=monitor_memory,
        daemon=True
    )
    monitor_thread.start()

    try:
        # Lazy loading
        df = dd.read_csv(
            DATA_FILE,
            blocksize=BLOCK_SIZE,
            assume_missing=True
        )

        print(f"Partitions: {df.npartitions}")

        # Build lazy computations
        total_rows_lazy = df.map_partitions(len).sum()
        total_fare_lazy = df["fare_amount"].sum()
        valid_fares_lazy = df["fare_amount"].count()

        print("Lazy computation graph created.")
        print("Executing optimized graph...\n")

        # Execute together to share computation
        with ProgressBar():
            total_rows, total_fare, valid_fares = dask.compute(
                total_rows_lazy,
                total_fare_lazy,
                valid_fares_lazy,
                scheduler="threads",
                num_workers=2,
                optimize_graph=True
            )

    finally:
        stop_event.set()
        monitor_thread.join()

    execution_time = time.perf_counter() - start

    average_fare = total_fare / valid_fares
    peak_ram = memory_stats["peak"] / GIB

    results = f"""
TASK 3: DASK DATAFRAME
------------------------------
Status: SUCCESS
Total rows: {total_rows:,}
Partitions: {df.npartitions}
Block size: {BLOCK_SIZE}

Total fare: {total_fare:.2f}
Valid fares: {valid_fares:,}
Average fare: {average_fare:.4f}

Execution time: {execution_time:.2f} seconds
Peak RAM: {peak_ram:.2f} GiB
------------------------------
"""

    print(results)

    (RESULTS_DIR / "task3_results.txt").write_text(
        results,
        encoding="utf-8"
    )


if __name__ == "__main__":
    main()
