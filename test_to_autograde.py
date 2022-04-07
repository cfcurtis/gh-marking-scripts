import unittest
import sys
import os
import json

def flatten_tests(tests):
    """
    Flattens a list of tests into a single list.
    """
    flat_list = []
    for test in tests:
        if hasattr(test, '__iter__'):
            flat_list += flatten_tests(test)
        else:
            flat_list.append(test)

    return flat_list

def get_tests(folder):
    """
    Returns a list of all the test methods in a folder.
    """
    test_list = []
    for test in unittest.TestLoader().discover(folder):
        for test_case in test:
            test_list.append(test_case)
    
    # flatten the list
    return flatten_tests(test_list)

def main():
    folder = sys.argv[1]
    tests = get_tests(folder)
    autograding = {'tests': []}
    for test in tests:
        test_case = {
            'name': test.shortDescription(),
            "setup": "",
            "run": "python3 -m unittest " + test.id(),
            "input": "",
            "output": "",
            "comparison": "included",
            "timeout": 5,
            "points": 1
        }
        autograding['tests'].append(test_case)
    
    # create the .github folder if it doesn't already exist
    gh_folder = os.path.join(folder, '.github')
    if not os.path.exists(gh_folder):
        os.mkdir(gh_folder)
    classroom_folder = os.path.join(gh_folder, 'classroom')
    if not os.path.exists(classroom_folder):
        os.mkdir(classroom_folder)
    
    with open(os.path.join(classroom_folder, 'autograding.json'), 'w') as f:
        json.dump(autograding, f, indent=2)

if __name__ == '__main__':
    main()