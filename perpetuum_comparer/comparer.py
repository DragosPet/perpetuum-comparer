"""Main module for comparing two datasets."""

import logging
import pandas as pd
import numpy as np
from datetime import datetime
from tabulate import tabulate
from termcolor import colored
from perpetuum_comparer.utils import logging_setup

log = logging_setup(logging.INFO)


class DataComparer:
    """Main comparison class."""

    def __init__(
        self,
        test_name: str,
        primary_df: pd.DataFrame,
        secondary_df: pd.DataFrame,
        line_id: str,
    ) -> None:
        """Initialize Data Comparer.

        Args:
        test_name(str): Test Name used to generate the final reports.
        primary_df(pd.DataFrame): Primary dataframe for comparison.
        secondary_df(pd.DataFrame): Secondary dataframe for comparison.
        line_id(str): Line identifier for dataframes.

        Returns:
        None
        """
        self.test_name = test_name
        self.primary_df = primary_df
        self.secondary_df = secondary_df
        self.line_id = line_id
        self.exclusive_primary_indexes = []
        self.exclusive_secondary_indexes = []

    def structural_comparison(self) -> bool:
        """Initialize Data Comparer.

        Args:

        Returns:
        match_flag(bool): Bool flag that will specify if there is any structural difference between the 2 dataframes.
        """
        self.structural_matches = []
        self.structural_diffs = []
        checked_keys = []
        if self.primary_df.empty:
            log.error("Primary DataFrame is empty. Stopping structural comparison!")
            return False
        if self.secondary_df.empty:
            log.error("Secondary DataFrame is empty. Stopping structural comparison!")
            return False
        log.info("Starting structural comparison of the 2 dataframes.")
        match_flag = True
        primary_columns = self.primary_df.dtypes.to_dict()
        secondary_columns = self.secondary_df.dtypes.to_dict()

        for key in primary_columns.keys():
            if secondary_columns.get(key):
                if primary_columns[key] == secondary_columns[key]:
                    self.structural_matches.append((key, primary_columns[key]))
                else:
                    self.structural_diffs.append((key, primary_columns[key]))
                    match_flag = False
            else:
                self.structural_diffs.append((key, primary_columns[key]))
                match_flag = False
            checked_keys.append(key)

        for key in secondary_columns.keys():
            if key not in checked_keys:
                self.structural_diffs.append((key, secondary_columns[key]))
                match_flag = False
        return match_flag

    def display_structural_comparison(self) -> None:
        print("Structural matches :")
        print(
            tabulate(
                self.structural_matches,
                headers=["Column", "Pandas Data Type"],
                tablefmt="grid",
                showindex="always",
            )
        )
        print("Structural Differences :")
        print(
            tabulate(
                self.structural_diffs,
                headers=["Column", "Pandas Data Type"],
                tablefmt="grid",
                showindex="always",
            )
        )

    def content_comparison(self) -> None:
        log.info("Comparing data counts")
        primary_count = self.primary_df.shape[0]
        secondary_count = self.secondary_df.shape[0]
        if primary_count == secondary_count:
            print(f"Data counts matches between datasets : {primary_count} recs !")
        else:
            print(
                f"Data counts different between datasets : PRIMARY : {primary_count} VS SECONDARY : {secondary_count} !"
            )
        if self.structural_matches:
            filter_cols = [x[0] for x in self.structural_matches]
            print(filter_cols)
            subset_primary_df = self.primary_df[filter_cols]
            subset_secondary_df = self.secondary_df[filter_cols]

        differences = []
        for index, rec in subset_primary_df.iterrows():
            index_dict = {"index": index, "key_differences": [], "secondary_val": []}
            if rec[self.line_id] in subset_secondary_df[self.line_id].to_list():
                compared_secondary_df = subset_secondary_df[
                    subset_secondary_df[self.line_id] == rec[self.line_id]
                ]
                compared_secondary_dict = compared_secondary_df.to_dict(
                    orient="records"
                )[0]
                for key in filter_cols:
                    if rec[key] != compared_secondary_dict[key]:
                        print(rec[key], compared_secondary_dict[key])
                        index_dict["key_differences"].append(key)
                        index_dict["secondary_val"].append(compared_secondary_dict[key])
                        differences.append(index_dict)
            else:
                self.exclusive_primary_indexes.append(index)

        # get secondary df exclusive lines
        for ind, x in subset_secondary_df.iterrows():
            if x[self.line_id] not in subset_primary_df[self.line_id].to_list():
                self.exclusive_secondary_indexes.append(ind)
        return differences

    def generate_reports(self, differences_array: dict) -> "tuple[pd.DataFrame]":
        reports = []
        if len(differences_array) > 0:
            for entry in differences_array:
                report_line = self.primary_df.iloc[[entry["index"]]].to_dict(
                    orient="records"
                )[0]
                for diff in entry["key_differences"]:
                    report_line[diff] = (
                        f"{report_line[diff]}/{colored(entry['secondary_val'][0],'red')}"
                    )
                reports.append(report_line)

        diff_reports = pd.DataFrame(reports, columns=self.primary_df.columns)
        primary_exclusive_reports = pd.DataFrame(
            self.primary_df.iloc[self.exclusive_primary_indexes]
        )
        secondary_exclusive_reports = pd.DataFrame(
            self.secondary_df.iloc[self.exclusive_secondary_indexes]
        )
        return (diff_reports, primary_exclusive_reports, secondary_exclusive_reports)


if __name__ == "__main__":
    df1 = pd.DataFrame(
        {"col1": [1, 2, 3, 4], "col2": [3, 5, 6, 8], "col3": [8, 1, 3, 7]},
        columns=["col1", "col2", "col3"],
    )

    df2 = pd.DataFrame(
        {
            "col1": [1, 2, 3, 5],
            "col2": [3, 7, 6, 8],
            "col3": [6, 1, 3, 2],
            "col4": [7, 2, 4, 0],
        },
        columns=["col1", "col2", "col3", "col4"],
    )

    print(df1)
    print(df2)

    dc = DataComparer("test", df1, df2, "col1")
    matching_flag = dc.structural_comparison()
    diffs = dc.content_comparison()
    print(dc.exclusive_primary_indexes, dc.exclusive_secondary_indexes)
    dc.display_structural_comparison()
    (common_diffs, primary_exclusive, secondary_exclusive) = dc.generate_reports(diffs)

    print(
        tabulate(
            common_diffs,
            headers=common_diffs.columns,
            tablefmt="grid",
            showindex="always",
        )
    )
    print(
        tabulate(
            primary_exclusive,
            headers=primary_exclusive.columns,
            tablefmt="grid",
            showindex="always",
        )
    )
    print(
        tabulate(
            secondary_exclusive,
            headers=secondary_exclusive.columns,
            tablefmt="grid",
            showindex="always",
        )
    )
