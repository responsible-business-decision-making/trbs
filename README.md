# 🦋 Vlinder 

Welcome to the open-source GitHub repository of the Responsible Business Simulator (tRBS) model based on the book. 
This model is available in Python package vlinder. The name vlinder means "butterfly" in Dutch. It symbolizes 
the transformation of _trbs_, pronounced quickly as _trups_ (= caterpillar in Dutch), and the ability to see things 
from a new perspective, much like how the package helps users transform raw data into insightful decision making.

## 🔗 This repository
This repo allows users to understand the framework and interact with the model, providing the opportunity to experiment, 
evaluate, and collaborate. The tRBS model is designed to simulate the impact of business decisions on sustainability 
and social responsibility. By open-sourcing the code, we promote transparency and invite contributions from 
researchers and practitioners.

Amongst others, it contains: 
- A **Jupyter notebook** demo that showcases the most important functions of the vlinder package
- All **core functionality** of the Responsible Business Simulator model
- A variety of demo cases that can be found [here](https://github.com/responsible-business-decision-making/trbs/tree/main/src/vlinder/data)

## 💻 Local set-up

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

### That's all! 🎉 ###
You're now able to play around with the `vlinder_demo` notebook.

## 🔗 Contributing

Please refer to the [CONTRIBUTING.MD](https://github.com/responsible-business-decision-making/trbs/blob/main/CONTRIBUTING.md)
document on how you can help developing vlinder

## 📖 Code of Conduct
- 😃 Be kind
- 🤗 Be welcoming
- ❌ Don't be a jerk
