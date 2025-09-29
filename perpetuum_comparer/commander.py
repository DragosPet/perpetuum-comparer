import configargparse
import logging
import pandas as pd
from termcolor import colored
from tabulate import tabulate
from perpetuum_comparer.utils import read_df_from_path, logging_setup, export_df_to_path
from perpetuum_comparer.comparer import DataComparer

parser = configargparse.ArgParser()

parser.add(
    "-pd",
    "--primary_df",
    required=True,
    help="Path to primary Dataset that will be compared.",
)

parser.add(
    "-sd",
    "--secondary_df",
    required=True,
    help="Path to secondary Dataset that will be compared.",
)

parser.add(
    "-li",
    "--line_id",
    required=True,
    help="Line Identifier column (unique and not null).",
)

parser.add(
    "-tn",
    "--test_name",
    required=False,
    default="COMPARISON",
    help="Comparison Name, defaults to COMPARISON.",
)

parser.add(
    "-sh",
    "--show_details",
    required=False,
    default="N",
    help="Show comparison details tabular data",
)

parser.add(
    "-ep",
    "--export_path",
    required=False,
    default=None,
    help="Export test report to given path as CSV file",
)

parser.add(
    "-ll",
    "--log_level",
    required=False,
    default="error",
    help="Logging level, defaults to error.",
)


def main():
    args = parser.parse_args()
    primary_df_path = args.primary_df
    secondary_df_path = args.secondary_df
    test_name = args.test_name
    line_id = args.line_id
    log_level = args.log_level
    export_path = args.export_path
    if args.show_details.upper() == "N":
        show_details = False
    else:
        show_details = True
    if log_level == "info":
        ll = logging.INFO
    else:
        ll = logging.ERROR
    log = logging_setup(ll)

    # import dataframes
    df_p = read_df_from_path(primary_df_path, log=log, input_format="csv")
    df_s = read_df_from_path(secondary_df_path, log=log, input_format="csv")

    # initialize data comparer
    dc = DataComparer(
        test_name=test_name, primary_df=df_p, secondary_df=df_s, line_id=line_id
    )

    # run comparison logic
    structural_match = dc.structural_comparison()
    if structural_match:
        print(
            f"The compared datasets are identical from a structural perspective ! - {colored('OK','green')} ✅"
        )

        diffs = dc.content_comparison()

        if len(diffs) == 0 and len(dc.exclusive_primary_indexes) == 0:
            print(
                f"No content differences between the compared datasets ! - {colored('OK','green')} ✅"
            )
        else:
            print("There are differences in the content of the 2 dataframes. ❌ ")
            (common_diffs, primary_exclusive, secondary_exclusive, export_diffs) = (
                dc.generate_reports(diffs)
            )

            difference_count = (
                common_diffs.shape[0]
                + primary_exclusive.shape[0]
                + secondary_exclusive.shape[0]
            )
            percentage_of_difference = (
                round(difference_count / dc.primary_df.shape[0], 4) * 100
            )

            print(
                f"There is a {colored(round(percentage_of_difference,2), 'red')} % difference between the 2 files."
            )

            if not show_details:
                if export_path:
                    export_df_to_path(
                        export_diffs, log, export_path=export_path, file_name=test_name
                    )
                return None

            print(
                tabulate(
                    common_diffs,
                    headers=common_diffs.columns,
                    tablefmt="grid",
                    showindex="always",
                )
            )
            if primary_exclusive.shape[0] > 0 :
                print("Records that are only present in the Primary dataset : ")
                print(
                    tabulate(
                        primary_exclusive,
                        headers=primary_exclusive.columns,
                        tablefmt="grid",
                        showindex="always",
                    )
                )
            else:
                print(f"No records that are only present in the Primary dataset. - {colored('OK','green')} ✅")

            if secondary_exclusive.shape[0] > 0:
                print("Records that are only present in the Secondary dataset : ")
                print(
                    tabulate(
                        secondary_exclusive,
                        headers=secondary_exclusive.columns,
                        tablefmt="grid",
                        showindex="always",
                    )
                )
            else:
                print(f"No records that are only present in the Secondary dataset. - {colored('OK','green')} ✅")

            if export_path:
                export_df_to_path(
                    export_diffs, log, export_path=export_path, file_name=test_name
                )
    else:
        if len(dc.structural_matches) == 0:
            print(
                "There are no structural matches between the compared datasets. They are completely different. ❌ "
            )
        else:
            print(
                "There are structural differences between the compared datasets, but also common fields. ❌ "
            )
            dc.display_structural_comparison()

            diffs = dc.content_comparison()

            if len(diffs) == 0 and len(dc.exclusive_primary_indexes) == 0:
                print("No content differences between the compared datasets. - {colored('OK','green')} ✅")
            else:
                print("There are differences in the content of the 2 dataframes. ❌ ")
                (common_diffs, primary_exclusive, secondary_exclusive, export_diffs) = (
                    dc.generate_reports(diffs)
                )

                difference_count = (
                    common_diffs.shape[0]
                    + primary_exclusive.shape[0]
                    + secondary_exclusive.shape[0]
                )
                percentage_of_difference = (
                    round(difference_count / dc.primary_df.shape[0], 4) * 100
                )

                print(
                f"There is a {colored(round(percentage_of_difference,2), 'red')} % difference between the 2 files."
                )

                if not show_details:
                    return None

                print(
                    tabulate(
                        common_diffs,
                        headers=common_diffs.columns,
                        tablefmt="grid",
                        showindex="always",
                    )
                )

                if primary_exclusive.shape[0] > 0 :
                    print("Records that are only present in the Primary dataset : ")
                    print(
                        tabulate(
                            primary_exclusive,
                            headers=primary_exclusive.columns,
                            tablefmt="grid",
                            showindex="always",
                        )
                    )
                else:
                    print(f"No records that are only present in the Primary dataset. - {colored('OK','green')} ✅")
                
                if secondary_exclusive.shape[0] > 0:
                    print("Records that are only present in the Secondary dataset : ")
                    print(
                        tabulate(
                            secondary_exclusive,
                            headers=secondary_exclusive.columns,
                            tablefmt="grid",
                            showindex="always",
                        )
                    )
                else:
                    print(f"No records that are only present in the Secondary dataset. - {colored('OK','green')} ✅")

                if export_path:
                    export_df_to_path(
                        export_diffs, log, export_path=export_path, file_name=test_name
                    )


if __name__ == "__main__":
    main()
