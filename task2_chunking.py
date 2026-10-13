
import os
import time
import threading
from pathlib import Path

import pandas as pd
import psutil

# Configuration
BASE_DIR = Path(__file__).resolve().parent
DATA_FILE = BASE_DIR / "data" / "train.csv"
RESULTS_DIR = BASE_DIR / "results"
CHUNK_SIZE = 100_000

GIB = 1024 ** 3

# Memory monitoring
process = psutil.Process(os.getpid())
stop_event = threading.Event()
peak_memory = 0


def monitor_memory():
    global peak_memory

    while not stop_event.is_set():
        ram = process.memory_info().rss
        peak_memory = max(peak_memory, ram)
        stop_event.wait(0.1)


def main():
    RESULTS_DIR.mkdir(exist_ok=True)

    if not DATA_FILE.exists():
        print("Dataset not found!")
        return

    total_rows = 0
    total_fare = 0.0
    valid_fares = 0
    chunk_count = 0

    print("TASK 2: PANDAS CHUNKING")
    print(f"Chunk size: {CHUNK_SIZE:,}")
    print("Processing dataset...\n")

    monitor_thread = threading.Thread(
        target=monitor_memory,
        daemon=True
    )

    start = time.perf_counter()
    monitor_thread.start()

    try:
        for chunk in pd.read_csv(
            DATA_FILE,
            chunksize=CHUNK_SIZE
        ):
            total_rows += len(chunk)
            chunk_count += 1

            total_fare += chunk["fare_amount"].sum()
            valid_fares += chunk["fare_amount"].count()

            if chunk_count % 25 == 0:
                elapsed = time.perf_counter() - start

                print(
                    f"Chunks: {chunk_count} | "
                    f"Rows: {total_rows:,} | "
                    f"Time: {elapsed:.2f}s",
                    flush=True
                )
    finally:
        stop_event.set()
        monitor_thread.join()

    execution_time = time.perf_counter() - start
    average_fare = total_fare / valid_fares

    results = f"""
TASK 2: PANDAS CHUNKING
------------------------------
Status: SUCCESS
Total rows: {total_rows:,}
Chunks processed: {chunk_count}
Chunk size: {CHUNK_SIZE:,}

Total fare: {total_fare:.2f}
Valid fares: {valid_fares:,}
Average fare: {average_fare:.4f}

Execution time: {execution_time:.2f} seconds
Peak RAM: {peak_memory / GIB:.2f} GiB
------------------------------
"""

    print(results)

    (RESULTS_DIR / "task2_results.txt").write_text(
        results,
        encoding="utf-8"
    )


if __name__ == "__main__":
    main()
