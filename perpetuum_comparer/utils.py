import logging
import os
import pandas as pd


def logging_setup(log_level: int) -> logging.Logger:
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
        datefmt="%Y-%m-%dT%H:%M:%S%z",
    )
    log = logging.getLogger(__name__)
    return log


def test_valid_path(input_path: str) -> bool:
    """Given input path, check if it exists."""
    valid_flag = False
    if os.path.exists(input_path):
        valid_flag = True
    return valid_flag


def read_df_from_path(
    input_path: str, log: logging.Logger, input_format: str = "csv"
) -> pd.DataFrame:
    """Given input file path, read file content and return data Pandas DataFrame."""
    output_data = pd.DataFrame()
    if test_valid_path(input_path):
        log.info(f"Path {input_path} available. Reading data file.")
        if input_format == "csv":
            output_data = pd.read_csv(input_path)
        else:
            log.error(
                "Unable to read data. Invalid format provided. Returning empty DataFrame."
            )
    else:
        log.error(
            "Unable to read data. Invalid path provided. Returning empty DataFrame."
        )
    return output_data
