# Functionality models for the Cooling Systems Cascade (CSC) Scenario in CDCM

This repository contains the core abstractions that enable a user to create functionality models required to define and study disruption scenarios using the CDCM Language. 

These component/system level abstractions that specify the functionality models of the habitat system models with models of their safety-controls are described in  are used to define the behavior of systems/components that are studied in the CSC scenarios. These functionality models are organised in `csc_systems` package.

A set of core-abstractions simplify the definition of these functionality models by giving the users access to constructors and selectors that automatically construct common, repeating model patterns required to specify models of such complex systems. These procedures form the _core-abstractions_ of the CSC Functionality models and are packaged in `cdcm_csc`.

More documentation of the effort is maintained [here](https://tinyurl.com/cdcm-docs)


# 2.1- Installation (macOS)

To use this package, you need to first install  [`cdcm_execution`](https://github.com/sjdyke-reth-institute/cdcm_execution) Python package.

Briefly, here are the steps one must follow:

- Install `conda` and ensure it is discoverable from your system path
- Create a `conda` virtual environment with Python 3.9 and [JAX](https://github.com/google/jax)
- Install the `cdcm_execution` Python package

If you need access to the RETHi Github organization, please contact [R Murali Krishnan](mailto:mrajase@purdue.edu).

Once you have installed the `cdcm_execution` Python package in your `conda` virtual environment, confirm that the `cdcm` package is installed properly, then importing the `cdcm` module in your Python interpreter should not have any error.

```zsh
(<cdcm-venv-name>)$ python3
Python 3.9.18
[Clang 14.0.6 ] :: Anaconda, Inc. on darwin
Type "help", "copyright", "credits" or "license" for more information.
>>> from cdcm import *
>>> ...
```

Once you have confirmed the installation of the `cdcm` Python package, proceed as follows,

## 2.1a - Installation (Windows)

Windows is not a first world citizen of JAX [here](https://github.com/google/jax/issues/438). The only way we have managed to make this package work with Windows is by following the instructions provided in [this Stackoverflow discussion](https://stackoverflow.com/a/72499565/2845052).

## 2.2- Installation for developing more System Models


For users looking to develop more system/component functionality models, obtain access to the `cdcm_csc` repository. Please contact either [Rashi Jain](mailto:jain356@purdue.edu) or [R Murali Krishnan](mailto:mrajase@purdue.edu), if you don't have access already.

Then execute the following command in your command line to install the `cdcm_csc` package in your `conda` virtual environment

```
(<cdcm-venv-name>)$ pip install git+https://github.com/sjdyke-reth-institute/cdcm_csc.git
```


## 2.3- Installation for developers

For more experience users, you may also do a `develop` install of the `cdcm_csc` package by

- Cloning the `cdcm_csc` repository to an appropriate local path
```
$ git clone https://github.com/sjdyke-reth-institute/cdcm_csc.git
``` 
- Performing a `develop` install as follows
```
$ cd cdcm_csc/
$ pip install -e .
```

Python will automatically reload the package as and when you make changes to the files in the package.


## 2.4- Verify Installation

Verify the installation by executing the following program in the Python interpreter.
This program specifies a `system` with a damageable and aging component in the Python interpreter

```zsh
(cdcm-venv-name>)$ python3
Python 3.9.18
[Clang 14.0.6 ] :: Anaconda, Inc. on darwin
Type "help", "copyright", "credits" or "license" for more information.
>>> from cdcm import *
>>> with System(name="system") as system:
        clock = make_clock(dt=1.0, units="hours")
        # A damageable component with default health value = 1.0
        damageable_component = make_component("damageable_component", nominal_health=1.0)
        # An aging component that has an aging_rate of 0.1/hr
        aging_component = make_component("aging_component", clock=clock, aging_rate=0.1)
>>> print(system)
```