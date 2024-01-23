from operator import attrgetter
from pathlib import Path
from typing import Any, Callable

import matplotlib.pyplot as plt

from benchmark.runner import benchmark
from benchmark.utils import run

ROOT = Path(__file__).parent


async def main() -> None:
    def _base_plt_format(subplt: plt.Subplot, y_label: str) -> None:
        subplt.set_ylabel(y_label)
        subplt.grid(which="major", linewidth=1)
        subplt.grid(which="minor", linewidth=0.2)
        subplt.minorticks_on()
        subplt.set_xlim(min(concurrency), max(concurrency))

    concurrency = [
        *range(1, 10),
        *range(10, 50, 2),
        *range(50, 100, 5),
        *range(100, 200, 10),
        *range(200, 501, 25),
    ]

    results = [await benchmark(requests=1000, concurrency=c) for c in concurrency]

    fig, (diff_plt, mean_plt, median_plt, max_plt, min_plt) = plt.subplots(5, figsize=(15, 30))

    diff_plt.plot(concurrency, [a.mean / b.mean for a, b in results])
    _base_plt_format(diff_plt, y_label="Diff (times)")

    def _format_plat(subplt: plt.Subplot, key: str) -> None:
        getkey: Callable[[Any], float] = attrgetter(key)

        subplt.plot(concurrency, [getkey(a) for a, _ in results], label="default")
        subplt.plot(concurrency, [getkey(b) for _, b in results], label="async-safe")
        subplt.legend()

        _base_plt_format(subplt, y_label=f"{key.title()} (ms)")

    _format_plat(mean_plt, "mean")
    _format_plat(median_plt, "median")
    _format_plat(max_plt, "max")
    _format_plat(min_plt, "min")

    median_plt.set_xlabel("Concurrency")

    plt.savefig(ROOT / "benchmark.png")


if __name__ == "__main__":
    run(main())
