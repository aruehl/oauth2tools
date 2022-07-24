# Packaging

## useful links
* https://packaging.python.org/en/latest/guides/using-testpypi/
* https://martin-thoma.com/software-development-stages/

## preparation
    py -m pip install --upgrade build
    py -m pip install --upgrade twine

## build the package
    py -m build

## upload the package
    py -m twine upload --repository pypi dist/oauth2tools-*
