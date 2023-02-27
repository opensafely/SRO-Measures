# SRO-Measures

You can run this project via [Gitpod](https://gitpod.io) in a web browser by clicking on this badge: [![Gitpod ready-to-code](https://img.shields.io/badge/Gitpod-ready--to--code-908a85?logo=gitpod)](https://gitpod.io/#https://github.com/opensafely/SRO-Measures)

[View on OpenSAFELY](https://jobs.opensafely.org/repo/https%253A%252F%252Fgithub.com%252Fopensafely%252FSRO-Measures)

Details of the purpose and any published outputs from this project can be found at the link above.

The contents of this repository MUST NOT be considered an accurate or valid representation of the study or its purpose. 
This repository may reflect an incomplete or incorrect analysis with no further ongoing work.
The content has ONLY been made public to support the OpenSAFELY [open science and transparency principles](https://www.opensafely.org/about/#contributing-to-best-practice-around-open-science) and to support the sharing of re-usable code for other subsequent users.
No clinical, policy or safety conclusions must be drawn from the contents of this repository.

# About the OpenSAFELY framework

The OpenSAFELY framework is a Trusted Research Environment (TRE) for electronic
health records research in the NHS, with a focus on public accountability and
research quality.

Read more at [OpenSAFELY.org](https://opensafely.org).

# Licences
As standard, research projects have a MIT license. 

# Local Development

For local (non-Docker) development, first install [pyenv][] and execute:

```sh
pyenv install $(pyenv local)
```

Then, execute:

```sh
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip

# Either one or the other of the following
pip install -r requirements.txt
pip install -r requirements.dev.txt # For also running bin/codestyle.sh

# For QA
bin/codestyle.sh .
```
[pyenv]: https://github.com/pyenv/pyenv

## Tests

If you have a local development environment,
then the following command will write pytest's output to the terminal:

```sh
python -m pytest
```

You can also pass test modules, classes, and methods to pytest:

```sh
python -m pytest tests/test_notebooks_utilities.py::TestDropIrrelevantPractices::test_irrelevant_practices_dropped
```

If you don't have a local development environment,
then the following command will write pytest's output to *metadata/run_tests.log*.

```sh
opensafely run run_tests
```
