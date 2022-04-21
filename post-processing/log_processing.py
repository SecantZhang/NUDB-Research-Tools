import re
import argparse
import pandas as pd

"""
dictionary structure: 
log_dict = {
    maintest_name_1: {
        subtest_name_1: {
            "runtime": <time>, 
            "unit": <unit>, 
            "operators": {
                operators_name_1: [{ "runtime": <time>, "unit": <unit> }, 
                                   { "runtime": <time>, "unit": <unit> }],
                oparators_name_2: [{ "runtime": <time>, "unit": <unit> }, 
                                   { "runtime": <time>, "unit": <unit> }]
            }
        }, 
        subtest_name_2: {
            ...
        }
    }, 
    maintest_name_2: {
        ...
    }
}
"""


def log_parser(log_file: list):
    log_dict: dict = {}
    curr_maintest_name: str = None
    curr_subtest_name: str = None
    for curr_log in log_file:
        # extracting the main information for subtest under each main tests.
        if curr_log[:12] == "[ RUN      ]":
            maintest_name, subtest_name = [i for i in re.split('[\' .,()\n]', curr_log[12:]) if i != '']
            curr_maintest_name = maintest_name
            curr_subtest_name = subtest_name
            if maintest_name not in log_dict:
                log_dict[maintest_name] = {}

        if curr_log[:12] == "[       OK ]":
            maintest_name, subtest_name, time, unit = [i for i in re.split('[\' .,()\n]', curr_log[12:]) if i != '']
            if subtest_name not in log_dict[maintest_name]:
                log_dict[maintest_name][subtest_name] = {
                    "runtime": time,
                    "unit": unit,
                    "operators": {}
                }
            else:
                log_dict[maintest_name][subtest_name]["runtime"] = time
                log_dict[maintest_name][subtest_name]["unit"] = unit

        # extract the operator information for each subtests.
        if curr_log[:18] == "Current operator: ":
            operator_name, runtime, unit = curr_log[18:].split()
            operator_name = operator_name.split(":")[0]
            unit = unit.split(".")[0]
            if curr_subtest_name not in log_dict[curr_maintest_name]:
                log_dict[curr_maintest_name][curr_subtest_name] = {"operators": {operator_name: [{"runtime": runtime, "unit": unit}]}}
            else:
                if operator_name in log_dict[curr_maintest_name][curr_subtest_name]["operators"]: 
                    log_dict[curr_maintest_name][curr_subtest_name]["operators"][operator_name].append({"runtime": runtime, "unit": unit})
                else: 
                    log_dict[curr_maintest_name][curr_subtest_name]["operators"][operator_name] = [{"runtime": runtime, "unit": unit}]

    return log_dict


def log_writer(log_dict: dict, output_file: str):
    column_names: list = ["maintest", "subtest", "operator", "time", "unit"]
    output_list = []
    for maintest_name, maintest_dict in log_dict.items():
        output_list.append([maintest_name, "", "", "", ""])
        for subtest_name, subtest_dict in log_dict[maintest_name].items():
            output_list.append([maintest_name, subtest_name, "", subtest_dict["runtime"], subtest_dict["unit"]])
            if subtest_dict["operators"]:  # check if the subtest_dict["operators"] is empty
                for operator_name, operator_list in subtest_dict["operators"].items():
                    for operator_dict in operator_list: 
                        output_list.append([maintest_name, subtest_name, operator_name, operator_dict["runtime"], operator_dict["unit"]])

    parsed_df = pd.DataFrame(output_list, columns=column_names)
    parsed_df.to_csv(output_file, index=False)


# TODO: Update the readme file accordingly.
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--log-file', type=str, dest='log_file')
    parser.add_argument('--output', type=str, dest='output_file', default=None)
    args = parser.parse_args()
    print(args)

    # TODO: implement the corner case.
    if args.output_file is None:
        print("output_file is None")
    with open(args.log_file, 'r') as f:
        log_file = [line for line in f]

    parsed_log = log_parser(log_file)
    log_writer(parsed_log, args.output_file)
