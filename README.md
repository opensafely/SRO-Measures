# SRO-Measures

## Local Development

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

# About the OpenSAFELY framework

The OpenSAFELY framework is a secure analytics platform for
electronic health records research in the NHS.

Instead of requesting access for slices of patient data and
transporting them elsewhere for analysis, the framework supports
developing analytics against dummy data, and then running against the
real data *within the same infrastructure that the data is stored*.
Read more at [OpenSAFELY.org](https://opensafely.org). 

*STP level reports have been generated for all STPs where TPP software coverage exceeds 10%
