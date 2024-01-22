#!/usr/bin/bash

function run_benchmark() {
    python -m benchmark.run --runs 1000 --concurrency $1 --output md
}

echo "
Benchmark for simple application:
\`\`\`py
$(cat benchmark/app.py)
\`\`\`
"

for conn in 1 10 20 40 50 75 100;
  do
    echo "
## Concurrency $conn

$(run_benchmark $conn)
"
  done