from perpetuum_comparer.comparer import DataComparer
from perpetuum_comparer.utils import logging_setup, read_df_from_path
import logging

def test_structural_match():
    logger = logging_setup(logging.INFO)
    df_p = read_df_from_path("test_files/docA.csv", log=logger, input_format="csv")
    df_s = read_df_from_path("test_files/docB.csv", log=logger, input_format="csv")
    dc = DataComparer(
        "unit_tests",
        df_p,
        df_s,
        "A"
    )
    assert(dc.structural_comparison() == True)

def test_structural_mismatch():
    logger = logging_setup(logging.INFO)
    df_p = read_df_from_path("test_files/docA.csv", log=logger, input_format="csv")
    df_s = read_df_from_path("test_files/docX.csv", log=logger, input_format="csv")
    dc = DataComparer(
        "unit_tests",
        df_p,
        df_s,
        "A"
    )
    assert(dc.structural_comparison() == False)

def test_content_comparison_match():
    logger = logging_setup(logging.INFO)
    df_p = read_df_from_path("test_files/docA.csv", log=logger, input_format="csv")
    df_s = read_df_from_path("test_files/docA.csv", log=logger, input_format="csv")
    dc = DataComparer(
        "unit_tests",
        df_p,
        df_s,
        "A"
    )

    dc.structural_comparison()
    diffs = dc.content_comparison()

    assert(len(diffs) == 0)