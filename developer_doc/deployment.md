# Long version:
* [Python Packaging User Guide](https://packaging.python.org/tutorials/packaging-projects/)

# Short version:
1- Creating the package files:
* Create/edit the setup.py (build script for setuptools).
* Create/edit the LICENSE file (license text for your Python Package).
* create/edit the README.md¶ file (used to generate the html summary you see at the bottom of projects).
* Note: We use the following file structure (your project name = example_pkg):  
/Git_Projects  
&nbsp; &nbsp; /example_pkg  
&nbsp; &nbsp; &nbsp; &nbsp; /example_pkg # All stuffs of the example_pkg  are there (in /Git_Projects/example_pkg/example_pkg/)  
&nbsp; &nbsp; setup.py  
&nbsp; &nbsp; LICENSE  
&nbsp; &nbsp; README.md  

2- Make sure you have the latest versions of setuptools, wheel and twine installed:
* python3 -m pip install --user --upgrade setuptools wheel twine  

3- Generating distribution archives:
* python3 setup.py sdist bdist_wheel # From the same directory where setup.py is located
* Note1: Make sure you have nothing in the /Git_Projects/example_pkg/dist/ folder (or that it does not exist) before launching the previous command.
* Note2: The previous command will generate /Git_Projects/example_pkg/dist/, /Git_Projects/example_pkg/build/ and /Git_Projects/example_pkg/example_pkg.egg-info/ directories.

4- Uploading the distribution archives:
* On Test PyPI:
  * python3 -m twine upload --repository-url https://test.pypi.org/legacy/ dist/* # From /Git_Projects/example_pkg/
  
* On the real Python Package Index:
  * python3 -m twine upload dist/* # From /Git_Projects/example_pkg/
  
5- To avoid problems in the future, delete the /Git_Projects/example_pkg/dist/, /Git_Projects/example_pkg/build/ and /Git_Projects/example_pkg/example_pkg.egg-info/ directories.
