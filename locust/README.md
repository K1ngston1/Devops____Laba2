# HMP Load Testing with Locust

This directory contains load testing scripts for the HearMyPaper (HMP)
application using [Locust](https://locust.io/).

The tests are based on a [HMP load testing strategy](https://github.com/staleread/hmp-docs/blob/main/reports/pw05_load-testing-strategy.md).

## Setup

Create test data before running tests:

```bash
./env up --host <SERVER_HOST> --credentials /path/to/admin.bin
```

This creates:
- 80 test students (`student000@hmp.test` through `student079@hmp.test`)
- 20 test instructors (`instructor000@hmp.test` through `instructor019@hmp.test`)
- 30 test projects (prefixed with `$TEST$`)
- Random assignments of students to 3-5 projects

## Running Tests

### Quick Start

```bash
./run --host <SERVER_HOST>
```

Open [http://localhost:8089](http://localhost:8089) to:
- Start/stop tests
- Adjust user count dynamically
- View real-time metrics and charts
- Download reports

## Cleanup

Remove test data after testing:

```bash
./env down --host <SERVER_HOST> --credentials /path/to/admin.bin
```
