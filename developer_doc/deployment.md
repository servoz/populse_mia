# How to test the deployment (cf. https://packaging.python.org/tutorials/packaging-projects/)

Use these several commands (from where the setup.py file is located):

# Generating distribution archives
First update setuptools and wheel:
          python3 -m pip install --user --upgrade setuptools wheel
Make sure you have nothing in the dist/ folder (or that it does not exist) and run:
          python3 setup.py sdist bdist_wheel

# Uploading the distribution archives
Update or install twine:
          python3 -m pip install --user --upgrade twine
Upload the archives under dist/:
          twine upload --repository-url https://test.pypi.org/legacy/ dist/*
