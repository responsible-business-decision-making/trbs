# Model: Responsible Business Simulator

Welcome to the open-source GitHub repository of the Responsible Business Simulator (RBS) model based on the book. 
This repo allows users to understand the framework and interact with the model, providing the opportunity to experiment, 
evaluate, and collaborate. The RBS model is designed to simulate the impact of business decisions on sustainability 
and social responsibility. By open-sourcing the code, we promote transparency and invite contributions from 
researchers and practitioners.

## In this repository
This repository contains 
- A **Jupyter notebook** to work with the model in an interactive way
- The **core functions** of the RBS model
- The following demo cases: beerwiser 

## Local set-up

**Step 1:** connect with the repository. If you either need to set-up git and/or 
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

**Step 3:** configure the pre-commit file. This file helps you adhere to a clean coding style and checks
amongst others for PEP8 violations. 
```
pre-commit install
```


**Step 4:** open the Jupyter notebook.
```
jupyter notebook
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



## Code of Conduct
- Be kind
- Be welcoming
- Don't be a jerk
