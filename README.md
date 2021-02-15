# Notebooks for "Covid Aftershocks" dashboards

This repository is for work-in-progress analysis of data in the OpenSafely network, elucidating the 
impacts on routine care of the Covid pandemic. The aim is to produce dashboards at 
national, regional and practice level. The notebooks here will largely be protoypes 
of dashboards. Notebooks covering vaccinations are [here](https://github.com/opensafely/vaccinations-dashboard). 
Practice dashboards will ultimately be produced within EHR software for GPs to access securely.

## Data sources
OpenSafely datasets (largely primary care records and emergency care, may 
also include additional secondary care data at a later date).

## How to view the notebooks

Notebooks live in the `notebooks/` folder (with an `ipynb`
extension). You can most easily view them [on
nbviewer](https://nbviewer.jupyter.org/github/ebmdatalab/<repo>/tree/master/notebooks/),
though looking at them in Github should also work.

To do development work, you'll need to set up a local jupyter server
and git repository - see notes below and `DEVELOPERS.md` for more detail.

## How to cite

XXX Please change to either a paper (if published) or the repo. You may find it helpful to use Zenodo DOI (see [`DEVELOPERS.md`](DEVELOPERS.md#how-to-invite-people-to-cite) for further information)

## Running these notebooks

Create a file `environ.txt` in the root and set the SQL server details/credentials as follows:
`DBCONN="DRIVER={ODBC Driver 17 for SQL Server};SERVER=[servername];DATABASE=[dbname];UID=[your_UID];PWD=[your_pw]"`. 

This is referred to in `run.py` so run the notebook using command `py run.py` in Windows (outside of the server) rather than using `run.exe`.

Within the server, add `--env-file environ.txt` to the docker run command

The credentials are loaded into notebooks as follows:
```python
dbconn = os.environ.get('DBCONN', None).strip('"')
def closing_connection(dbconn):
    cnxn = pyodbc.connect(dbconn)
    try:
        yield cnxn
    finally:
        cnxn.close()
```

## Getting started re-running these notebooks

This project uses reproducible, cross-platform
analysis notebook, using Docker.  It also includes:

* configuration for `jupytext`, to support easier code review
* cross-platform startup scripts
* best practice folder structure and documentation

Developers and analysts using this repo should
refer to [`DEVELOPERS.md`](DEVELOPERS.md) for instructions on getting
started. 

If you have not yet installed Docker, please see the [`INSTALLATION_GUIDE.md`](INSTALLATION_GUIDE.md)
