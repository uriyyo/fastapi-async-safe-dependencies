#!/usr/bin/bash

function run_benchmark() {
    python -m benchmark.run --runs 250 --concurrency "$1" --output md
}

echo "
Benchmark for simple application:
\`\`\`py
$(cat benchmark/app.py)
\`\`\`
"

for conn in 1 10 25 50 100;
  do
    echo "
## Concurrency $conn

$(run_benchmark $conn)
"
  done