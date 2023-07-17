# Model: Responsible Business Simulator

Welcome to the open-source GitHub repository of the Responsible Business Simulator (RBS) model based on the {LINK_TO_BOOK}. 
This repo allows users to understand the framework and interact with the model, providing the opportunity to experiment, 
evaluate, and collaborate. The RBS model is designed to simulate the impact of business decisions on sustainability 
and social responsibility. By open-sourcing the code, we promote transparency and invite contributions from 
researchers and practitioners.

## In this repository
This repository contains 
- _(model/tRBS.ipynb)_ A **Jupyter notebook** to work with the model in an interactive way
- The **core functions** of the RBS model

## Local set-up (TBD)

**Step 1:** connect with the repository. If you either need to set-up git and/or 
authenticate with GitHub, see [GitHub's manual](https://docs.github.com/en/get-started/quickstart/set-up-git).
```
git clone https://github.com/responsible-business-decision-making/tRBS_model.git
```

**Step 2:** install all required dependencies with ```pipenv```. You might need to install ```pipenv``` if you have
not used this before. 
```
pip install pipenv
pipenv install
```

**Step 3:** configure the pre-commit file. This file helps you adhere to a clean coding style and checks
amongst others for PEP8 violations. 
```
pre-commit install
```


**Step x:** open the Jupyter notebook.
```
jupyter notebook --notebook-dir=\model
```

**(optional) A1:** Create a new branch if you want to work on a new feature, bug or case.
```
git checkout -b 'NAME-OF-YOUR-BRANCH'
```

**(optional) A2:** Run all `pytest` tests in the `/model` folder.
```
python -m pytest
```



## Code of Conduct
- Be kind
- Be welcoming
- Don't be a jerk
