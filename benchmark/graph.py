from pathlib import Path

import matplotlib.pyplot as plt

from benchmark.runner import benchmark
from benchmark.utils import run

ROOT = Path(__file__).parent


async def main() -> None:
    concurrency = [*range(1, 101)]
    results = [await benchmark(runs=20, concurrency=c) for c in concurrency]

    fig, (diff_plt, mean_plt) = plt.subplots(2, figsize=(15, 8))
    fig.suptitle("Benchmark")

    diff_plt.plot(concurrency, [a.mean / b.mean for a, b in results])
    diff_plt.set_ylabel("Diff")
    diff_plt.grid(which="major", linewidth=1)
    diff_plt.grid(which="minor", linewidth=0.2)
    diff_plt.minorticks_on()
    diff_plt.set_xlim(1, 100)

    mean_plt.plot(concurrency, [a.mean for a, _ in results], label="default")
    mean_plt.plot(concurrency, [b.mean for _, b in results], label="async safe")
    mean_plt.set_xlabel("Concurrency")
    mean_plt.set_ylabel("Mean")
    mean_plt.grid(which="major", linewidth=1)
    mean_plt.grid(which="minor", linewidth=0.2)
    mean_plt.minorticks_on()
    mean_plt.set_xlim(1, 100)
    mean_plt.legend()

    plt.savefig(ROOT / "benchmark.png")


if __name__ == "__main__":
    run(main())
