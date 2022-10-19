# SRO-Measures

This is the code and configuration for the OpenSAFELY Service Restoration Observatory (SRO) key measures of primary care activity.

You can run this project via [Gitpod](https://gitpod.io) in a web browser by clicking on this badge: [![Gitpod ready-to-code](https://img.shields.io/badge/Gitpod-ready--to--code-908a85?logo=gitpod)](https://gitpod.io/#https://github.com/opensafely/pincer-measures)

* The preprint is [here (to add)](https://www.medrxiv.org/content/10.1101/2022.10.17.22281058v1).
* Analysis outputs, including charts, crosstabs, etc, can be found [here](https://jobs.opensafely.org/datalab/service-restoration-observatory/sro-measures/outputs/).
* If you are interested in how we defined our variables, take a look at the [study definition](analysis/study_definition.py); this is written in `python`, but non-programmers should be able to understand what is going on there
* If you are interested in how we defined our code lists, look in the [codelists folder](./codelists/).
* Developers and epidemiologists interested in the framework should review [the OpenSAFELY documentation](https://docs.opensafely.org)

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
