import re
import argparse
import pandas as pd


def log_parser(log_file: list):
    log_list: list = []
    for curr_log in log_file:
        test_pattern: str = curr_log[:12]
        if test_pattern == "[       OK ]":
            log_list.append([i for i in re.split('[\' .,()\n]', curr_log[12:]) if i != ''])
    return log_list


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
    parsed_df = pd.DataFrame(parsed_log, columns=["testname", "subtest", "time (ms)", "unit"])
    parsed_df.to_csv(args.output_file, index=False)
