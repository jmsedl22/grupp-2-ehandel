# Group 2 E-commerce analysis report
Group assignment for a course in PYthon programming. The project aims to build an e-commerce report in a Jupyter Notebook, given sample data from a csv file.

## Setting up the project

### Dependencies
- Python version 3.14.17
- Git

Older Python versions or operating systems other than Windows 11 have not been verified.

### 1. Creating a virtual environment
```sh
python -m venv .venv
```
### 2. Activating the virtual environment
Using Windows PowerShell:
```sh
.\.venv\Scripts\Activate.ps1
```
On macOS or Linux:
```sh
source .venv/bin/activate
```

### 3. Installing dependencies
```sh
python -m pip install -r requirements.txt
```

### 4. Opening the notebook
```sh
python -m jupyterlab
```

## Workflow
Our agreed-upon workflow is as follows:

- Read the issue specification.
- Create a local branch from an updated main (git switch main, git pull, git switch -c [name]/[description-of-work]).
- Solve the issue.
- Test the solution.
- Make a commit with a descriptive message (git commit -m "[description]").
- Push your code to remote (git push).
- Open a pull request link the issue by adding "References #[issue number]" or "Solves #[issue number]" to the PR description. (If you write 'solves' or 'closes', GitHub will automatically close the issue. Write 'references' if you don't want it closed yet.)
- Briefly describe your changes.
- Let the group examine and approve your changes.
  - Fix any follow-up.
- Merge the pull request when it is approved.
- Close the issue by marking it as 'done.'
