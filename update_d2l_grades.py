import pandas as pd
import sys
from pathlib import Path

# Points needed to pass each lab
PASSING_POINTS = {
    1: 1,
    2: 2
}

def update_grades(d2l_csv: pd.DataFrame, github_csv_folder: Path) -> pd.DataFrame:
    """
    Loads all the csvs in the github_csv_folder and updates the d2l_csv with the number of labs completed.
    """
    lab_col = [col for col in d2l_csv.columns if "Lab Exercises" in col][0]
    d2l_csv["roster_identifier"] = d2l_csv["First Name"] + " " + d2l_csv["Last Name"]

    # Zero out the lab column
    d2l_csv[lab_col] = 0
    n_labs = 0
    for csv in github_csv_folder.glob("*.csv"):
        # kind of convoluted, but it works
        this_lab = pd.read_csv(csv)
        lab_num = int(csv.name[3:5])
        
        # Convert to pass/fail based on passing points for the lab
        this_lab[f"lab{lab_num}"] = this_lab["points_awarded"] >= PASSING_POINTS[lab_num]
        this_lab = this_lab[["roster_identifier", f"lab{lab_num}"]]

        # Merge the lab data into the d2l_csv and add to the lab total column
        d2l_csv = d2l_csv.merge(this_lab, on="roster_identifier", how="left")
        d2l_csv[lab_col] += d2l_csv[f"lab{lab_num}"].fillna(0)
        d2l_csv.drop(columns=[f"lab{lab_num}"], inplace=True)
        n_labs += 1

    # Update the total number of labs (MaxPoints) - not sure if D2L parses this
    new_lab_col = f"Lab Exercises Points Grade <Numeric MaxPoints:{n_labs} Weight:10>"
    d2l_csv.rename(columns={lab_col: new_lab_col}, inplace=True)
    d2l_csv.drop(columns=["roster_identifier"], inplace=True)
    
    return d2l_csv

def main():
    if len(sys.argv) < 3:
        print("Usage: update_d2l_grades d2l_csv github_csv_folder")
        sys.exit()

    d2l_csv = pd.read_csv(sys.argv[1])
    gh_folder = Path(sys.argv[2])
    d2l_csv = update_grades(d2l_csv, gh_folder)
    d2l_csv.to_csv(gh_folder.parent / "updated_d2l_grades.csv", index=False)


if __name__ == "__main__":
    main()