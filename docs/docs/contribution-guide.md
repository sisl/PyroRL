# Contribution Guide

To get started on contributing, check out the below guide on how to get the package installed locally, how to update this documentation website, and more.

## How to Set-Up

To set up our codebase, create a virtual environment and install a local copy of the package.

```bash
python3 -m venv env
source env/bin/activate
cd wildfire_evac/
pip install .
```

## Package Deployment

All of the details of the package can be found in `wildfire_evac/setup.py`. This file defines attributes such as the name of the package, the version number, and the dependencies needed to use the package.

Next, you build the distribution archives. Archives are compressed files that allow the package to be deployed across multiple platforms. You run the following command to generate the distribution files:

```bash
python3 setup.py sdist
```

Using the above command should generate a `dist` folder, which contains the compressed distribution files.

Finally, we can publish it to the official PyPi repository using a package called `twine`:

```bash
twine upload dist/*
```

Doing the * will upload all of the compressed distribution files, so ideally, we would clear out all of them and then have only one set of distribution files.

## Testing

We use [`pytest`](https://docs.pytest.org/en/7.4.x/) for our backend tests. To keep the state of our package as small as possible, we don't include `pytest`. Thus, make sure to install the package before running.

```bash
pip install pytest
python3 -m pytest -s
```

## Continuous Integration

We use [GitHub Actions](https://github.com/features/actions) to automatically run our entire test suite upon each `push`. Check out the file `.github/workflows/testing.yml` to edit this job.

## Documentation

We use [MkDocs](https://www.mkdocs.org/) for our documentation. To set up and make edits to our documentation, first install the MkDocs package:

```bash
pip install mkdocs
```

Then, making sure you're in the same directory as the `mkdocs.yml` configuration file, you can start the server by running the command:

```bash
mkdocs serve
```

For more tips, check out their [documentation](https://www.mkdocs.org/).
