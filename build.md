# Packaging

## useful links

* https://packaging.python.org/en/latest/guides/using-testpypi/
* https://martin-thoma.com/software-development-stages/

## build and upload

### github

#### versioning and tagging

    python package.py <major|minor|patch>

#### build and upload the package to pypi

create a release on [github](https://github.com/aruehl/oauth2tools/releases/new)

### local

#### preparation

    python -m pip install --upgrade build
    python -m pip install --upgrade twine

#### build the package

    python -m build

#### upload the package to pypi

    python -m twine upload --repository pypi dist/oauth2tools-*
