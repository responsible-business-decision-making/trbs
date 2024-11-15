_Hello! Thank you for looking into contributing into vlinder. To make this as easy as possible 
for all parties involved, please follow the steps below._ 

## 🔗 How do I Contribute? 

### 1. Please open an Issue
The issue should contain a description of what you're trying to add/fix/change. 

### 2. Create a branch of type DESCRIPTION/ISSUE NUMBER
Fork the project and create a feature branch to work on your add/fix/change. Please name the branch using the 
following format: DESCRIPTION/ISSUE NUMBER

### 3. Squash your commits into one 
Squash all your commits into a single commit with a clear commit message. 

### 4. Open a pull request
Open a pull request with reference to the original issue. Provide a concise description of what you did and how your 
changes fixed the issue. Note that a PR requires **at least two** approvals from maintainers before it can be merged.

## 🔍 How is my PR reviewed? 
A pull request is reviewed by at least two maintainers. These maintainers will validate the pull request using the checklist outlined below.

0. To locally test the change in the vlinder package, first run: 
    ```
    pip install . 
    ```

1. The code passes all **unit tests** in the `tests` folder. If unit tests are changed there must be a valid reason to 
do so. For new scripts and/or logic unit tests must be added. <br><br> To run the unit tests: 
    ```
    python -m pytest
    ```

2. The code satisfies PEP8 and is **properly formatted**. The format rules can be found in the 
 `.pre-commit-config.yaml`-file. <br><br> To run this for all files, simply run
    ```
    pre-commit run --all-files
    ```
   The score does not need to be 100%, but easy fixes should be resolved. 
<br><br>
3. If a new **data model** is added, at least the following should be present:
   1. A **xlsx**, **csv** and **json** file of the new data model. You only have to build one format and can use the 
    `transform` function to generate the other two. 
   2. Add at least one relevant unit test to `test_evaluate_all_dependencies` for the new case.
   3. The `README.md`-file in the data folder has been updated. 
<br><br>
4. If the **vlinder_demo notebook** has been changed, ensure that 
   1. it still uses beerwiser as default case
   2. the kernel is clean. Click 'Kernel' > 'Restart & Clear Output'