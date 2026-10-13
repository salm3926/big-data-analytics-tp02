
import os
import sys
import time
import subprocess
from pathlib import Path

import pandas as pd
import psutil

# --------------------------------
# Configuration
# --------------------------------

BASE_DIR = Path(__file__).resolve().parent

DATA_FILE = BASE_DIR / "data" / "train.csv"

RESULTS_DIR = BASE_DIR / "results"
LOG_FILE = RESULTS_DIR / "task1_log.txt"

GIB = 1024 ** 3


# --------------------------------
# Worker: Standard Pandas
# --------------------------------

def worker():

    print("TASK 1: TRADITIONAL PANDAS")
    print("Loading the entire CSV into RAM...", flush=True)

    start = time.perf_counter()

    try:

        df = pd.read_csv(DATA_FILE)

        elapsed = time.perf_counter() - start

        print("\nSTATUS: SUCCESS", flush=True)
        print(f"Rows loaded: {len(df):,}", flush=True)
        print(f"Columns: {len(df.columns)}", flush=True)
        print(f"Execution time: {elapsed:.2f}s", flush=True)

    except MemoryError as error:

        elapsed = time.perf_counter() - start

        print("\nSTATUS: MEMORY ERROR", flush=True)
        print(f"Exception: {type(error).__name__}", flush=True)
        print(f"Details: {error}", flush=True)
        print(f"Execution time: {elapsed:.2f}s", flush=True)

        sys.exit(2)

    except Exception as error:

        elapsed = time.perf_counter() - start

        print("\nSTATUS: ERROR", flush=True)
        print(f"Exception: {type(error).__name__}", flush=True)
        print(f"Details: {error}", flush=True)
        print(f"Execution time: {elapsed:.2f}s", flush=True)

        sys.exit(3)


# --------------------------------
# Monitor all Python processes
# --------------------------------

def get_memory_usage(parent):

    try:
        processes = [parent] + parent.children(recursive=True)
    except (psutil.NoSuchProcess, psutil.AccessDenied):
        return 0, 0

    total_rss = 0
    total_private = 0

    for process in processes:

        try:
            info = process.memory_info()

            total_rss += info.rss
            total_private += getattr(info, "private", 0)

        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue

    return total_rss, total_private


# --------------------------------
# Main experiment
# --------------------------------

def main():

    if not DATA_FILE.exists():
        print("ERROR: Dataset not found!")
        return

    RESULTS_DIR.mkdir(exist_ok=True)

    system = psutil.virtual_memory()

    print("TASK 1: OOM CHALLENGE")
    print("------------------------------")
    print(f"Dataset size: {DATA_FILE.stat().st_size / GIB:.2f} GiB")
    print(f"Total RAM: {system.total / GIB:.2f} GiB")
    print(f"Available RAM: {system.available / GIB:.2f} GiB")
    print("Automatic memory stop: DISABLED")
    print("------------------------------\n")

    peak_ram = 0
    peak_private = 0

    start = time.perf_counter()

    with open(LOG_FILE, "w", encoding="utf-8") as log:

        process = subprocess.Popen(
            [sys.executable, "-u", __file__, "--worker"],
            stdout=log,
            stderr=subprocess.STDOUT
        )

        parent = psutil.Process(process.pid)

        while process.poll() is None:

            ram, private = get_memory_usage(parent)

            peak_ram = max(peak_ram, ram)
            peak_private = max(peak_private, private)

            elapsed = time.perf_counter() - start

            available = psutil.virtual_memory().available / GIB

            print(
                f"\rTime: {elapsed:.1f}s | "
                f"RAM: {ram / GIB:.2f} GiB | "
                f"Private: {private / GIB:.2f} GiB | "
                f"Available: {available:.2f} GiB",
                end="",
                flush=True
            )

            time.sleep(0.5)

        process.wait()

    elapsed = time.perf_counter() - start

    worker_log = LOG_FILE.read_text(encoding="utf-8")

    if "STATUS: MEMORY ERROR" in worker_log:
        status = "MEMORY ERROR"

    elif "STATUS: SUCCESS" in worker_log:
        status = "SUCCESS"

    elif "STATUS: ERROR" in worker_log:
        status = "ERROR"

    else:
        status = "PROCESS FAILED"

    results = f"""

--- TASK 1 FINAL RESULTS ---

Status: {status}
Dataset: NYC Taxi Fare Prediction

Dataset size: {DATA_FILE.stat().st_size / GIB:.2f} GiB
Total RAM: {system.total / GIB:.2f} GiB

Execution time: {elapsed:.2f} seconds
Peak RAM: {peak_ram / GIB:.2f} GiB
Peak Private Memory: {peak_private / GIB:.2f} GiB

Exit code: {process.returncode}

----------------------------
"""

    print(results)

    with open(LOG_FILE, "a", encoding="utf-8") as log:
        log.write(results)

    print("Log saved to:", LOG_FILE)


if __name__ == "__main__":

    if "--worker" in sys.argv:
        worker()
    else:
        main()
