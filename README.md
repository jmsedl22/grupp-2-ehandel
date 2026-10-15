# Group 2 E-commerce analysis report
Group assignment for a course in Python programming. The project aims to build an e-commerce report in a Jupyter Notebook, given sample data from a CSV file.

### Setup and execution
- Python 3 and Git are installed.
- The required Python version has not yet been decided.

From the repository root, run 
```
python -m venv
```
to create a virtual environment.

With the virtual environment activated, install JupyterLab by running
```
python -m pip install jupyterlab
```
Additional dependencies will be documented when necessary. 

## Goals
As per the assignment, the analysis part of this assignment aims to answer:
1. What sells? (Which categories generate the most income?)
2. Where do we sell? (Which cities account for the largest share of revenue?)
3. When do we sell? (Are there any clear time patterns for the given period?)
4. What does a typical order look like? (Average order value and spread.)
5. Top lists (Top 3 categories based on revenue.)
6. Deviations (Other patterns that stand out.) 

## Workflow
Our agreed-upon workflow is as follows:

1. Read the issue specification.
2. Create a local branch from an updated main. In order, run the following:
    - `git switch main`
    - `git pull --ff-only`
    - `git switch -c [name]/[description-of-work]`
3. Solve the issue.
4. Test the solution (the program must run).
5. Make a commit with a descriptive message:
    - `git commit -m "[description]"`
6. Push your code to remote (`git push`).
7. Open a pull request and link the issue by adding "References #[issue number]" or "Solves #[issue number]" to the PR description.
    - Writing 'Solves' or 'Closes' will automatically close the related issue when the PR is merged.
    - Writing 'References' will simply link the issue.
8. Briefly describe your changes in the pull request description.
9. Let the group examine and approve your changes.
    - Fix or address any feedback.
10. Merge the pull request when it is approved.

## Responsibilities
Individual responsibilities will be documented as they are decided. 

## Project structure
The project structure follows the proposed template given in the assignment description. 
```
grupp-2-ehandel/
├── data/
│   └── ecommerce_sales.csv   # Input dataset for the analysis
├── notebook/
│   └── ecommerce_sales.ipynb # Main analysis notebook (planned)
├── src/
│   ├── ecommerce.py          # E-commerce analysis logic (planned)
│   ├── io_utils.py           # Data loading and file handling (planned)
│   ├── metrics.py            # Sales metric calculations (planned)
│   └── viz.py                # Charts and visualizations (planned)
├── .gitignore
└── README.md
```
Reusable, generic Python code is found in `src/`, while the notebook contains goal-specific analysis and visualizations.
