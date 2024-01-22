from dataclasses import asdict, dataclass, fields, is_dataclass
from json import dumps
from typing import Any, Iterator, Literal

import click

from benchmark.runner import BenchmarkResult, BenchmarkTestSuite, benchmark
from benchmark.utils import run


@dataclass
class ResultRow:
    type: str
    default: float
    async_safe: float
    diff: float


def get_diff(a: float, b: float) -> str:
    diff = round(a / b, 2)

    if diff > 0:
        return f"x{diff} faster"
    if diff < 0:
        return f"x{diff} slower"

    return "0 same"


def _json_default(obj: Any) -> Any:
    if is_dataclass(obj):
        return asdict(obj)

    return str(obj)


def _json_output(rows: list[ResultRow]) -> None:
    print(dumps(rows, default=_json_default, indent=4))


_MD_COL_WIDTH = 15
_MD_HEADERS = ["Type", "Default", "Async Safe", "Diff"]


def _md_output_gen(rows: list[tuple[str, str, str, str]]) -> Iterator[str]:
    def _pad(s: str) -> str:
        return f"{s:<{_MD_COL_WIDTH}}"

    yield f"| {' | '.join(_pad(h) for h in _MD_HEADERS)} |"
    yield f"|{'|'.join('-' * (_MD_COL_WIDTH + 2) for _ in _MD_HEADERS)}|"

    for row in rows:
        yield f"| {' | '.join(_pad(r) for r in row)} |"


def _md_output(rows: list[ResultRow]) -> None:
    def _format_float(f: float) -> str:
        return f"{f:.2f}"

    def _format_time(f: float) -> str:
        return f"{_format_float(f)}ms"

    def _format_diff(diff: float) -> str:
        if diff > 0:
            return f"x{_format_float(diff)} faster"
        if diff < 0:
            return f"x{_format_float(diff)} slower"

        return "0 same"

    formatted_rows = [
        (
            row.type,
            _format_time(row.default),
            _format_time(row.async_safe),
            _format_diff(row.diff),
        )
        for row in rows
    ]

    print("\n".join(_md_output_gen(formatted_rows)))


@click.command()
@click.option(
    "-n",
    "--requests",
    default=10_000,
    help="Number of requests to perform",
)
@click.option(
    "-c",
    "--concurrency",
    default=10,
    help="Number of concurrent requests",
)
@click.option(
    "-s",
    "--suite",
    default=BenchmarkTestSuite.app,
    type=click.Choice([v.value for v in BenchmarkTestSuite]),
    help="Which test suite to run",
)
@click.option(
    "-o",
    "--output",
    default="json",
    type=click.Choice(["json", "md"]),
    help="Output format (json or markdown)",
)
def main(
    requests: int,
    concurrency: int,
    suite: BenchmarkTestSuite,
    output: Literal["json", "md"],
) -> None:
    suite = BenchmarkTestSuite(suite)
    default_run, async_safe_run = run(
        benchmark(
            requests=requests,
            concurrency=concurrency,
            suite=suite,
        )
    )

    rows: list[ResultRow] = []
    for field in fields(BenchmarkResult):
        default_val = getattr(default_run, field.name)
        async_safe_val = getattr(async_safe_run, field.name)

        rows.append(
            ResultRow(
                type=field.name,
                default=default_val,
                async_safe=async_safe_val,
                diff=default_val / async_safe_val,
            ),
        )

    if output == "json":
        _json_output(rows)
    else:
        _md_output(rows)


if __name__ == "__main__":
    main()
