## TP02 — Results Summary

| Method | Execution Time | Peak RAM |
|---|---:|---:|
| Standard Pandas | 120.49 s | 10.86 GiB |
| Pandas Chunking | 80.66 s | **0.16 GiB** |
| Dask DataFrame | **67.22 s** | 0.76 GiB |

**Fastest:** Dask DataFrame (67.22 s). **Lowest memory usage:** Pandas Chunking (0.16 GiB). Standard Pandas successfully loaded all 55,423,856 rows, without a `MemoryError`, but used much more memory. Chunking and Dask produced the same average taxi fare (**11.3450**).

**Note:** Standard Pandas was timed for full-file loading only, whereas Chunking and Dask also calculated aggregates; the timings are indicative, not a perfectly equivalent benchmark.

