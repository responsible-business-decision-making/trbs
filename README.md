# 🦋 Vlinder 

Welcome to the open-source GitHub repository of the Responsible Business Simulator (tRBS) model based on the book 
Roobeek, A; Swart, J.J.B. de; Plas, M. van der (2023), Responsible Business Decision Making – 
Strategic Impact Through Data and Dialogue, KoganPage, that can be found [here](https://www.koganpage.com/product/responsible-business-decision-making-9781398612280). 
This model is available in Python package vlinder. The name vlinder means "butterfly" in Dutch. It symbolizes 
the transformation of _trbs_, pronounced quickly as _trups_ (= caterpillar in Dutch), and the ability to see things 
from a new perspective, much like how the package helps users transform raw data into insightful decision making.

## 🔗 This repository
This repo allows users to understand the framework and interact with the model, providing the opportunity to experiment, 
evaluate, and collaborate. The tRBS model is designed to simulate the impact of business decisions on financial performance, sustainability 
and social responsibility. By open-sourcing the code, we promote transparency and invite contributions from 
researchers and practitioners.

Amongst others, this repo contains: 
- A **[Jupyter notebook](https://github.com/responsible-business-decision-making/trbs/blob/vlinder_demo.ipynb)** demo that showcases the most important functions of the vlinder package
- All **core functionality** of the Responsible Business Simulator model
- A variety of demo cases that can be found [here](https://github.com/responsible-business-decision-making/trbs/tree/main/src/vlinder/data)

## 💻 Working with the vlinder package via the **[Jupyter notebook](https://github.com/responsible-business-decision-making/trbs/blob/vlinder_demo.ipynb)**

Here we assume that you just want to install and import the vlinder package from Python Package Index and work with
the predefined Jupyter notebook **vlinder_demo.ipynb**. This means that you are not interested in the source code 
within the vlinder package.
To purpose of **vlinder_demo.ipynb** is to to illustrate the working of the vlinder package.
This file is the only file from this repository that you need for this use case.
There are many environments in which you may run Jupyter notebooks. In this example, we use using Google's free 
environment called Colaboratory. Note that a Google account is needed to access this environment. 

**Step 1:** Open Google's Colabotary by clicking on **[this](https://colab.research.google.com/)**.

**Step 2:** Choose "Open notebook -> GitHub" and enter **[this](https://github.com/responsible-business-decision-making/trbs/blob/vlinder_demo.ipynb)** url.

**Step 3:** Run the notebook by selecting "Run all" from the "Runtime" menu to see the results for the beerwiser case.

**Step 4:** (Optional) Adjust the notebook to see, e.g., results of other demo cases. 

## 💻 Local set-up (working directly with the underlying code of the vlinder package)

Here we assume that you want to contribute to the vlinder package by adjusting or and enriching its code base.

**Step 1:** Connect with the repository. If you either need to set-up git and/or 
authenticate with GitHub, see [GitHub's manual](https://docs.github.com/en/get-started/quickstart/set-up-git).
```
git clone https://github.com/responsible-business-decision-making/trbs.git
```

**Step 2:** Move inside the `trbs`-folder and install all required dependencies with ```pipenv```. 
You might need to install ```pipenv``` if you have not used this before. 
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
document for further guidance no how you can help developing vlinder

## 📖 Code of Conduct
- 😃 Be kind
- 🤗 Be welcoming
- ❌ Don't be a jerk
