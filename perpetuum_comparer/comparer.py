"""Main module for comparing two datasets."""
import logging
import pandas as pd
import numpy as np
from datetime import datetime
from tabulate import tabulate

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%S%z",
)
log = logging.getLogger(__name__)

class DataComparer:
    """Main comparison class."""
    def __init__(self, test_name:str, primary_df: pd.DataFrame, secondary_df: pd.DataFrame, line_id: str) -> None:
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

    def structural_comparison(self) -> bool:
        """Initialize Data Comparer.
        
        Args:
        
        Returns:
        match_flag(bool): Bool flag that will specify if there is any structural difference between the 2 dataframes.
        """
        self.structural_matches = []
        self.structural_diffs = []
        checked_keys = []
        if self.primary_df.empty :
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
                    self.structural_matches.append(
                        (key, primary_columns[key])
                    )
                else : 
                    self.structural_diffs.append(
                        (key, primary_columns[key])
                    )
                    match_flag = False
            else : 
                self.structural_diffs.append(
                    (key, primary_columns[key])
                )
                match_flag = False
            checked_keys.append(key)
        
        for key in secondary_columns.keys():
            if key not in checked_keys:
                self.structural_diffs.append(
                    (key, secondary_columns[key])
                )
                match_flag = False
        return match_flag
    
    def display_structural_comparison(self) -> None:
        print("Structural matches !")
        print(tabulate(
            self.structural_matches,
            headers=["Column", "Pandas Data Type"],
            tablefmt="grid",
            showindex="always"
        ))
        print("Structural Differences !")
        print(tabulate(
            self.structural_diffs,
            headers=["Column", "Pandas Data Type"],
            tablefmt="grid",
            showindex="always"
        ))
    
    def content_comparison(self) -> None:
        log.info("Comparing data counts")
        primary_count = self.primary_df.shape[0]
        secondary_count = self.secondary_df.shape[0]
        if primary_count == secondary_count : 
            print(f"Data counts matches between datasets : {primary_count} recs !")
        else : 
            print(f"Data counts different between datasets : PRIMARY : {primary_count} VS SECONDARY : {secondary_count} !")
        if self.structural_matches : 
            filter_cols = [x[0] for x in self.structural_matches]
            print(filter_cols)
            subset_primary_df = self.primary_df[filter_cols]
            subset_secondary_df = self.secondary_df[filter_cols]
        
        differences = []
        for index, rec in subset_primary_df.iterrows() :
            index_dict = {
                "index": index,
                "key_differences": []
            }
            compared_secondary_df = subset_secondary_df[subset_secondary_df[self.line_id] == subset_primary_df[self.line_id]]
            compared_secondary_dict = compared_secondary_df.to_dict(orient="records")[index]
            for key in filter_cols:
                if rec[key] != compared_secondary_dict[key]:
                    print(rec[key], compared_secondary_dict[key])
                    index_dict["key_differences"].append(key)
                    differences.append(index_dict)
        print(differences)
        return differences 


if __name__ == "__main__":
    df1 = pd.DataFrame({
        "col1": [1,2,3],
        "col2": [3,5,6],
        "col3": [8,1,3]
    },columns=["col1","col2","col3"])

    df2 = pd.DataFrame({
        "col1": [1,2,3],
        "col2": [3,7,6],
        "col3": [6,1,3],
    },columns=["col1","col2","col3"])

    print(df1)
    print(df2)

    dc = DataComparer("test", df1, df2,"col1")
    matching_flag = dc.structural_comparison()
    dc.content_comparison()
    dc.display_structural_comparison()
