# General Info

You can see the benchmark source code in [/benchmark/apps/db_app.py](https://github.com/uriyyo/fastapi-async-safe-dependencies/tree/main/benchmark/apps/db_app.py).

Basically, it's use asyncpg+sqlalchemy to simulate single db call.
It has simple class hierarchy with 2 services and 2 repositories.
It should be enough to simulate some kind of real application.

# Results

## Concurrency 1

| Type            | Default         | Async Safe      | Diff            |
|-----------------|-----------------|-----------------|-----------------|
| min             | 1.56ms          | 1.20ms          | x1.30 (faster)  |
| max             | 60.18ms         | 29.33ms         | x2.05 (faster)  |
| mean            | 1.84ms          | 1.39ms          | x1.32 (faster)  |
| median          | 1.72ms          | 1.30ms          | x1.32 (faster)  |


## Concurrency 10

| Type            | Default         | Async Safe      | Diff            |
|-----------------|-----------------|-----------------|-----------------|
| min             | 4.52ms          | 3.12ms          | x1.45 (faster)  |
| max             | 217.60ms        | 33.56ms         | x6.48 (faster)  |
| mean            | 10.92ms         | 7.24ms          | x1.51 (faster)  |
| median          | 10.09ms         | 5.80ms          | x1.74 (faster)  |


## Concurrency 25

| Type            | Default         | Async Safe      | Diff            |
|-----------------|-----------------|-----------------|-----------------|
| min             | 4.99ms          | 4.30ms          | x1.16 (faster)  |
| max             | 540.09ms        | 48.19ms         | x11.21 (faster) |
| mean            | 25.49ms         | 19.06ms         | x1.34 (faster)  |
| median          | 21.01ms         | 19.12ms         | x1.10 (faster)  |


## Concurrency 50

| Type            | Default         | Async Safe      | Diff            |
|-----------------|-----------------|-----------------|-----------------|
| min             | 4.45ms          | 13.02ms         | x0.34 (slower)  |
| max             | 1335.51ms       | 84.82ms         | x15.74 (faster) |
| mean            | 62.74ms         | 36.98ms         | x1.70 (faster)  |
| median          | 56.13ms         | 35.95ms         | x1.56 (faster)  |


## Concurrency 100

| Type            | Default         | Async Safe      | Diff            |
|-----------------|-----------------|-----------------|-----------------|
| min             | 20.26ms         | 34.07ms         | x0.59 (slower)  |
| max             | 2230.20ms       | 451.28ms        | x4.94 (faster)  |
| mean            | 142.35ms        | 94.35ms         | x1.51 (faster)  |
| median          | 99.37ms         | 74.39ms         | x1.34 (faster)  |
