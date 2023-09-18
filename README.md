<!-- Change these as needed -->

# Python Package Template

[![Unittest](https://github.com/PatrickMaul/config_loader_pkg/actions/workflows/unittest.yml/badge.svg)](https://github.com/PatrickMaul/config_loader_pkg/actions/workflows/unittest.yml)
[![codecov](https://codecov.io/gh/PatrickMaul/config_loader_pkg/graph/badge.svg?token=TSJ32TOKBJ)](https://codecov.io/gh/PatrickMaul/config_loader_pkg)

This repository is just a template for Python Packages.

## Table of Contents

<!-- TOC -->
* [Python Package Template](#python-package-template)
  * [Table of Contents](#table-of-contents)
  * [Project Setup](#project-setup)
  * [Running tests](#running-tests)
    * [Unittests & Coverage](#unittests--coverage)
    * [Code quality](#code-quality)
      * [Formatting with Black](#formatting-with-black)
      * [Linting with Flake8](#linting-with-flake8)
      * [Typ check with MyPy](#typ-check-with-mypy)
  * [Building](#building)
  * [Publishing](#publishing)
  * [Example Usage](#example-usage)
<!-- TOC -->

## Project Setup

To collaborate on the `package_name` module, follow these steps:

1. Open a terminal or command prompt.
2. Navigate to the directory where you want the project to reside.
3. Execute the following command to clone the repository:
   ```bash
   git clone repository-link
   ```
4. Navigate to the root directory of your project. `cd ./package_name`
5. Execute the one of following commands to install dependencies:  
   Using `requirements.txt`
   ```bash
   pip install -U pip
   pip install -r requirements.txt
   ```
   or using `pyproject.toml` (preferred)
   ```bash
   pip install -U pip
   pip install '.[dev]'
   ```

## Running tests

### Unittests & Coverage

To run unittests for the `package_name` module, follow these steps:

1. Open a terminal or command prompt.

2. Navigate to the root directory of the `package_name` module.

    - Execute the following command to run unit tests:
       ```bash
       python -m unittest discover test/tests/unit
       ```
      **Note**: You might need to export the `PYTHONPATH`.

    - Execute the following command to run coverage tests:  
      **Note**: Install command for `coverage`: `pip install -U coverage`
       ```bash
       coverage run --source=./pm_config_loader -m unittest discover ./test/tests/unit && coverage html -d test/tests/htmlcov
       ```
      **Note**: You might need to export the `PYTHONPATH`.

### Code quality

To run linter, formatter and typ checker for the `package_name` module, follow these steps:

1. Open a terminal or command prompt.

2. Navigate to the root directory of the `package_name` module.

#### Formatting with Black

Auto format your code by following running these command:

```bash
black .
```

#### Linting with Flake8

Lint your code by following running these command:

```bash
flake8 --config .flake8 .
```

#### Typ check with MyPy

Auto format your code by following running these command:

```bash
mypy .
```

## Building

To build the `package_name` module, follow these steps:

1. Navigate to the root directory of the `package_name` module.
2. Make sure you have `build` installed. If not, you can install it using the following command:
   ```bash
   pip install -U build
   ```

3. Execute the following command to build the module:
   ```bash
   python -m build
   ```

## Publishing

To upload the `package_name` module using `twine`, follow these steps:

1. Navigate to the root directory of the `package_name` module.
2. Make sure you have `twine` installed. If not, you can install it using the following command:
   ```bash
   pip install -U twine
   ```
3. Execute the following command to upload the module using `twine`:
   ```bash
   python -m twine upload -r testpypi -u <username> -p <password> dist/*
   ```

## Example Usage

Here is a simple example of how you can use the `package_name` module:

```python
# Example usage goes here
```