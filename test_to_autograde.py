import unittest
from unittest.mock import patch
from io import StringIO
import sys
from pathlib import Path
import json


def flatten_tests(tests):
    """
    Flattens a list of tests into a single list.
    """
    flat_list = []
    for test in tests:
        if hasattr(test, "__iter__"):
            flat_list += flatten_tests(test)
        else:
            flat_list.append(test)

    return flat_list


def parse_unittests(tests):
    """
    Converts the list of test cases from unittest into description/name pairs.
    """
    test_list = []
    for test in tests:
        test_list.append(
            {
                "setup": "",
                "description": test.shortDescription(),
                "command": f"python3 -m unittest {test.id()}",
            }
        )

    return test_list


def parse_pytests(tests):
    """
    Converts the list of test cases from pytest into description/name pairs.
    """
    test_list = []
    for test in tests:
        path, test_func = test.split("::")
        test_file = Path(path).name
        test_list.append(
            {
                "setup": "sudo -H pip3 install pytest",
                "description": test_func,
                "command": f"pytest{test_file}::{test_func}",
            }
        )

    return test_list


def get_tests(folder):
    """
    Returns a list of all the test methods in a folder.
    """
    # try unittests first
    test_list = []
    for test in unittest.TestLoader().discover(folder):
        for test_case in test:
            test_list.append(test_case)

    if len(test_list) > 0:
        return parse_unittests(flatten_tests(test_list))
    else:
        try:
            import pytest
        except ImportError:
            print("No unittests found and pytest not installed, exiting.")
            sys.exit()

        # get the list of tests from pytest. Pretty hacky.
        # Capture stdout, then run pytest.main
        stream = StringIO()
        with patch("sys.stdout", new=stream):
            pytest.main(["-q", folder, "--collect-only"])
            for line in stream.getvalue().splitlines():
                if "::" in line:
                    test_list.append(line)

        return parse_pytests(test_list)


def main():
    folder = sys.argv[1]
    tests = get_tests(folder)
    autograding = {"tests": []}
    for test in tests:
        test_case = {
            "name": test["description"],
            "setup": test["setup"],
            "run": test["command"],
            "input": "",
            "output": "",
            "comparison": "included",
            "timeout": 5,
            "points": 1,
        }
        autograding["tests"].append(test_case)

    # create the .github folder if it doesn't already exist
    gh_folder = Path(folder) / ".github"
    if not gh_folder.exists():
        gh_folder.mkdir()
    classroom_folder = gh_folder / "classroom"
    if not classroom_folder.exists():
        classroom_folder.mkdir()

    with open(classroom_folder / "autograding.json", "w") as f:
        json.dump(autograding, f, indent=2)


if __name__ == "__main__":
    main()
