import logging
import os
import pandas as pd
from datetime import datetime


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


def export_df_to_path(
    export_data: pd.DataFrame, log: logging.Logger, export_path: str, file_name: str
) -> None:
    """Given export file path and export data, save it to a local csv file."""
    if not os.path.exists(export_path):
        log.error("Provided path does not exist, stopping export !")
        exit(1)
    complete_export_file_name = (
        f"{export_path}/{file_name}_{datetime.now():%Y%m%d%H%M%S}.csv"
    )

    try:
        export_data.to_csv(complete_export_file_name, index=False, sep=",")
        log.info(f"Exported data to : {complete_export_file_name} !")
    except:
        log.error("Exception encountered while exporting file !")
