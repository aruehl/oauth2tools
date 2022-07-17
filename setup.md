# Packaging
https://packaging.python.org/en/latest/guides/using-testpypi/

## preparation
    py -m pip install --upgrade build
    py -m pip install --upgrade twine

## build the package
    py -m build

## upload the package
    py -m twine upload --repository pypi dist/oauth4cli-0.1.1it *