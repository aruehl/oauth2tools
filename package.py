import os
import shutil
import sys


def install_and_import(package):
    import pip
    import importlib
    pip.main(['install', package])
    globals()[package] = importlib.import_module(package)


try:
    import toml
except ImportError:
    install_and_import('toml')


def increment(i):
    return str(int(i)+1)


project = toml.load("pyproject.toml")
version = project.get('project').get('version').split(".")

if len(sys.argv) == 1:
    print(f"usage: {sys.argv[0]} mayor|minor|patch")
elif sys.argv[1] == "mayor":
    version[0] = increment(version[0])
    version[1] = "0"
    version[2] = "0"
elif sys.argv[1] == "minor":
    version[1] = increment(version[1])
    version[2] = "0"
elif sys.argv[1] == "patch":
    version[2] = increment(version[2])
else:
    print(f"usage: {sys.argv[0]} mayor|minor|patch")

version_string = ".".join(version)
project.get('project')['version'] = version_string

with open('pyproject.toml', 'w', encoding='utf8') as f:
    new_toml_string = toml.dump(project, f)

if os.path.isdir("dist"):
    shutil.rmtree("dist")

print(f"git commit -m 'new version {version_string}' pyproject.toml")
os.system(f"git commit -m \"new version {version_string}\" pyproject.toml")
os.system("git push")
exit(1)
os.system(f"git tag {version_string}")
os.system(f"git push origin {version_string}")

os.system("py -m build")
