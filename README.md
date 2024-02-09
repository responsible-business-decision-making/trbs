# Model: the Responsible Business Simulator

Welcome to the open-source GitHub repository of the Responsible Business Simulator (tRBS) model based on the book. This model is available in Python package vlinder.
This repo allows users to understand the framework and interact with the model, providing the opportunity to experiment, 
evaluate, and collaborate. The tRBS model is designed to simulate the impact of business decisions on sustainability 
and social responsibility. By open-sourcing the code, we promote transparency and invite contributions from 
researchers and practitioners.

## In this repository
This repository contains 
- A **Jupyter notebook** to work with the model in an interactive way
- The **core functions** of the tRBS model
- The following demo cases: beerwiser, DSM, IZZ and refugee case

## Local set-up

**Step 1:** Connect with the repository. If you either need to set-up git and/or 
authenticate with GitHub, see [GitHub's manual](https://docs.github.com/en/get-started/quickstart/set-up-git).
```
git clone https://github.com/responsible-business-decision-making/trbs.git
```

**Step 2:** Move inside the `trbs`-folder and install all required dependencies with ```pipenv```. You might need to install ```pipenv``` if you have
not used this before. 
```
cd trbs
pip install pipenv
pipenv install
pipenv shell
```

**Step 3:** Configure the pre-commit file. This file helps you adhere to a clean coding style and checks
amongst others for PEP8 violations. 
```
pre-commit install
```

**Step 4:** Open the Jupyter notebook.
```
jupyter notebook
```

**Step 5:** Import Path in Jupyter notebook to retrieve input data of the cases.
```
from pathlib import Path
```

**Step 6:** Import theResponsibleBusinessSimulator model from the core folder.
```
from core.trbs import TheResponsibleBusinessSimulator
```

**Step 7:** Retrieve the path of the data folder. This folder contains the input data of the cases.
```
path = Path.cwd() / 'data'
```

**Step 8:** Specify the file format of the input data and the case you want to investigate. By default we use Beerwiser case in xlsx format.
```
file_format = 'xlsx'
name = 'beerwiser'
```

**Step 9:** Call the Responsible Business Simulator to investigate the case.
```
case = TheResponsibleBusinessSimulator(path, file_format, name)
```

**(optional) A1:** Create a new branch if you want to work on a new feature, bug or case.
```
git checkout -b 'NAME-OF-YOUR-BRANCH'
```

**(optional) A2:** Run all `pytest` tests in the `/model` folder.
```
cd model
python -m pytest
```

## Vlinder package set-up

**Step 1:** Install required dependencies via pip install.
```
pip install pandas
pip install numpy
pip install openpyxl
pip install matplotlib
pip install xlsxwriter
```

**Step 2:** Install package vlinder.
```
pip install vlinder
```

**Step 3:** Install Jupyter notebook to work with the model in an interactive way.
```
pip install notebook
```

**Step 4:** Open the Jupyter notebook.
```
jupyter notebook
```

**Step 5:** Import required packages in Jupyter notebook to retrieve input data of the cases.
```
import os
from pathlib import Path
```

**Step 6:** Import package vlinder (abbreviated as vl) in Jupyter notebook.
```
import vlinder as vl
from vlinder import *
```

**Step 7:** Retrieve the path of the data folder from the package. This folder contains the input data of the cases.
```
path = Path(os.path.dirname(vlinder.__file__)) / 'data'
```

**Step 8:** Specify the file format of the input data and the case you want to investigate. By default we use Beerwiser case in xlsx format.
```
file_format = 'xlsx'
name = 'beerwiser'
```

**Step 9:** Call the Responsible Business Simulator to investigate the case.
```
case = TheResponsibleBusinessSimulator(path, file_format, name)
```

## Code of Conduct
- Be kind
- Be welcoming
- Don't be a jerk
