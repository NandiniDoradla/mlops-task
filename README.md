# MLOps Batch Job

## Overview

This project implements a minimal MLOps-style batch job in Python.

Features:
- Loads configuration from `config.yaml`
- Reads OHLCV data from `data.csv`
- Computes a rolling mean on the `close` column
- Generates binary trading signals
- Produces structured metrics in `metrics.json`
- Generates execution logs in `run.log`
- Runs locally and inside Docker

---

## Project Structure

```
mlops-task/
│── run.py
│── config.yaml
│── data.csv
│── requirements.txt
│── Dockerfile
│── README.md
│── metrics.json
│── run.log
```

---
## Requirements

- Python 3.9+
- Docker Desktop (for Docker execution)

## Local Run Instructions

### Install dependencies

```bash
pip install -r requirements.txt
```

### Run the application

```bash
python run.py \
--input data.csv \
--config config.yaml \
--output metrics.json \
--log-file run.log
```

---

## Docker Build and Run

### Build the Docker image

```bash
docker build -t mlops-task .
```

### Run the Docker container

```bash
docker run --rm mlops-task
```

---

## Example metrics.json

```json
{
  "version": "v1",
  "rows_processed": 10000,
  "metric": "signal_rate",
  "value": 0.4989,
  "latency_ms": 45,
  "seed": 42,
  "status": "success"
}
```
