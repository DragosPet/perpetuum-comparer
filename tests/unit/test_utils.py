from perpetuum_comparer.utils import path_validator, read_df_from_path, logging_setup

logger = logging_setup("info")

def test_path_validator_invalid_path():
    assert(path_validator("dummy_path") == False)

def test_path_validator_valid_path():
    assert(path_validator("test_files") == True)

def test_df_import_valid_dataset():
    test_df = read_df_from_path("test_files/docA.csv", log=logger)
    assert(test_df.shape[0] > 0)

def test_df_import_invalid_dataset():
    test_df = read_df_from_path("test_files/docY.csv", log=logger)
    assert(test_df.shape[0] == 0)    