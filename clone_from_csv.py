#!/usr/bin/env python
import csv
import sys
import subprocess
from pathlib import Path

def read_data(fname):
    """
    Reads the csv file and returns a list of dictionaries for each row.
    Skips over rows with no roster name (usually instructor account).
    """
    data = []
    with open(sys.argv[1],"r") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            if row["roster_identifier"]:
                data.append(row)
    return data
    
def clone_repos(data, dest_dir):
    """
    Clones the assignment repositories into destination directory.
    Renames to roster identifier with no spaces.
    """
    for row in data:
        dest_name = row["roster_identifier"].replace(" ", "")
        subprocess.call(["git", "clone", row["student_repository_url"], str(Path(dest_dir) / dest_name)])


def main():
    if len(sys.argv) < 2:
        print("Usage: clone_from_csv csv_file [destination_dir]")
        sys.exit()
    
    if len(sys.argv) > 2:
        dest_dir = sys.argv[2]
    else:
        dest_dir = "."

    data = read_data(sys.argv[1])
    clone_repos(data, dest_dir)


if __name__ == "__main__":
    main()