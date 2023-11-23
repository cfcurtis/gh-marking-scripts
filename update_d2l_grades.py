import pandas as pd
import sys
from pathlib import Path
import yaml
import subprocess

def update_overrides(d2l_csv: pd.DataFrame, params: dict, lab_col: str):
    """
    Performs any manual adjustments defined in params.
    """
    for username, val in params["overrides"].items():
        d2l_csv.loc[d2l_csv["roster_identifier"] == username, lab_col] += val

def update_grades(
    d2l_csv: pd.DataFrame, github_csv_folder: Path, params: dict
) -> pd.DataFrame:
    """
    Loads all the csvs in the github_csv_folder and updates the d2l_csv with the number of labs completed.
    """
    # D2L's naming is kind of dumb, so find the lab column
    lab_col = [col for col in d2l_csv.columns if params["lab_col"] in col][0]
    d2l_csv["roster_identifier"] = d2l_csv["First Name"] + " " + d2l_csv["Last Name"]

    # Zero out the lab column
    d2l_csv[lab_col] = 0
    n_labs = 0
    for csv in github_csv_folder.glob("*.csv"):
        # kind of convoluted, but it works
        this_lab = pd.read_csv(csv)
        lab_num = int(csv.name[-6:-4])

        # Convert to pass/fail based on passing points for the lab
        this_lab[f"lab{lab_num}"] = (
            this_lab["points_awarded"] >= params["passing_points"][lab_num - 1]
        )
        this_lab = this_lab[["roster_identifier", f"lab{lab_num}"]]

        # Merge the lab data into the d2l_csv and add to the lab total column
        d2l_csv = d2l_csv.merge(this_lab, on="roster_identifier", how="left")
        d2l_csv[lab_col] += d2l_csv[f"lab{lab_num}"].fillna(0)
        d2l_csv.drop(columns=[f"lab{lab_num}"], inplace=True)
        n_labs += 1

    update_overrides(d2l_csv, params, lab_col)
    d2l_csv.drop(columns=["roster_identifier"], inplace=True)

    return d2l_csv


def load_course_params(working_dir: Path) -> dict:
    """
    Loads the course_params.yml file in the working_dir
    """
    with open(working_dir / "course_params.yml", "r") as f:
        course_params = yaml.safe_load(f)

    return course_params


def download_gh_csvs(working_dir: Path, params: dict):
    """
    Downloads the csvs from github.
    """
    for lab, id in params["lab_ids"].items():
        subprocess.run(
            f"gh classroom assignment-grades -a {id} -f {working_dir / f'github_csvs/lab{lab:02d}.csv'}",
            shell=True,
        )


def main():
    if len(sys.argv) < 2:
        print("Usage: update_d2l_grades <path_to_autograde_dir>")
        sys.exit()

    working_dir = Path(sys.argv[1])

    # The d2l csv should have "GradesExport" in the name
    csv_path = list(working_dir.glob("*GradesExport*.csv"))[0]
    d2l_csv = pd.read_csv(csv_path)

    # working_dir should have a file named "course_params.yml"
    course_params = load_course_params(working_dir)
    download_gh_csvs(working_dir, course_params)

    d2l_csv = update_grades(d2l_csv, working_dir / "github_csvs", course_params)
    d2l_csv.to_csv(working_dir / "updated_d2l_grades.csv", index=False)


if __name__ == "__main__":
    main()
