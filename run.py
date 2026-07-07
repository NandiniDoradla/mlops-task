import argparse
import json
import logging
import os
import sys
import time

import numpy as np
import pandas as pd
import yaml


def load_config(config_path):
    """
    Load and validate the YAML configuration file.
    """

    # Check if config file exists
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Config file '{config_path}' not found.")

    # Read YAML
    with open(config_path, "r") as file:
        config = yaml.safe_load(file)

    # Check if config is empty
    if not config:
        raise ValueError("Config file is empty.")

    # Validate required keys
    required_keys = ["seed", "window", "version"]

    for key in required_keys:
        if key not in config:
            raise ValueError(f"Missing required config key: {key}")

    return config


def load_dataset(input_path):
    """
    Load and validate dataset.
    """

    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Input file '{input_path}' not found.")

    if os.path.getsize(input_path) == 0:
        raise ValueError("Input CSV file is empty.")

    try:
        df = pd.read_csv(input_path)

        # Handle malformed CSV where entire row is stored as one column
        if len(df.columns) == 1:
            column_name = df.columns[0]

            df = pd.read_csv(input_path, header=None, names=[column_name])

            df = df[column_name].str.split(",", expand=True)

            # Remove quotes from headers
            df.columns = df.iloc[0].str.replace('"', '', regex=False)

            # Remove header row
            df = df.iloc[1:].reset_index(drop=True)
            df.columns.name = None

            # Remove quotes from first and last columns
            df = df.apply(lambda col: col.str.replace('"', '', regex=False))

    except Exception as e:
        raise ValueError(f"Invalid CSV format: {e}")

    if df.empty:
        raise ValueError("CSV contains no data.")

    if "close" not in df.columns:
        raise ValueError("Missing required column: close")

    return df
def setup_logging(log_file):
    """
    Configure logging.
    """
    logging.basicConfig(
    filename=log_file,
    filemode="w",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    force=True
    )
def write_metrics(output_path, metrics):
    """
    Write metrics dictionary to a JSON file.
    """
    with open(output_path, "w") as file:
        json.dump(metrics, file, indent=2)
def write_error_metrics(output_path, version, error_message):
    """
    Write error metrics JSON.
    """
    metrics = {
        "version": version,
        "status": "error",
        "error_message": error_message
    }

    write_metrics(output_path, metrics)
def main():

    parser = argparse.ArgumentParser(description="MLOps Batch Job")

    parser.add_argument("--input", required=True, help="Input CSV file")
    parser.add_argument("--config", required=True, help="Configuration YAML file")
    parser.add_argument("--output", required=True, help="Output metrics JSON")
    parser.add_argument("--log-file", required=True, help="Log file")

    args = parser.parse_args()

    setup_logging(args.log_file)
    logging.info("Job started")

    start_time = time.time()

    try:

        # Print command line arguments
        print("Input File :", args.input)
        print("Config File:", args.config)
        print("Output File:", args.output)
        print("Log File   :", args.log_file)

        # Load configuration
        config = load_config(args.config)

        print("\nConfiguration Loaded Successfully")
        print("--------------------------------")
        print("Seed    :", config["seed"])
        print("Window  :", config["window"])
        print("Version :", config["version"])

        logging.info(
            f"Config loaded successfully: "
            f"seed={config['seed']}, "
            f"window={config['window']}, "
            f"version={config['version']}"
        )

        # Set random seed
        np.random.seed(config["seed"])

        # Load dataset
        df = load_dataset(args.input)

        print("\nDataset Loaded Successfully")
        print("---------------------------")
        print("Rows    :", len(df))
        print("Columns :", list(df.columns))

        logging.info(f"Rows loaded: {len(df)}")

        # Convert close column to numeric
        df["close"] = pd.to_numeric(df["close"])

        # Calculate rolling mean
        df["rolling_mean"] = df["close"].rolling(
            window=config["window"]
        ).mean()

        
        #print(df[["close", "rolling_mean"]].head(10))

        logging.info("Rolling mean calculated")

        # Generate signal
        df["signal"] = (
            (df["close"] > df["rolling_mean"])
            .fillna(False)
            .astype(int)
        )

        
        #print(df[["close", "rolling_mean", "signal"]].head(10))

        logging.info("Signal generation completed")

        # Calculate metrics
        rows_processed = len(df)
        signal_rate = round(df["signal"].mean(), 4)
        latency_ms = int((time.time() - start_time) * 1000)

        print("\nMetrics")
        print("--------")
        print("Rows Processed :", rows_processed)
        print("Signal Rate    :", signal_rate)
        print("Latency (ms)   :", latency_ms)

        logging.info(
            f"Metrics: rows={rows_processed}, "
            f"signal_rate={signal_rate}, "
            f"latency_ms={latency_ms}"
        )

        metrics = {
            "version": config["version"],
            "rows_processed": rows_processed,
            "metric": "signal_rate",
            "value": signal_rate,
            "latency_ms": latency_ms,
            "seed": config["seed"],
            "status": "success"
        }

        write_metrics(args.output, metrics)

        logging.info("Job completed successfully")

        print("\nmetrics.json created successfully.")
        print("\nFinal Metrics JSON:")
        print(json.dumps(metrics, indent=2))

    except Exception as e:

        logging.exception("Job failed")

        write_error_metrics(
            args.output,
            "v1",
            str(e)
        )

        print("\nJob Failed")
        print(e)

        sys.exit(1)


if __name__ == "__main__":
    main()