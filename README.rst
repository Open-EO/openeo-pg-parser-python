=======================
openeo-pg-parser-python
=======================


The package parses an openEO process graph (JSON) to a traversable Python object, containing input and dependencies for each node.


Description
===========

1. Install miniconda and clone repository:
------------------------------------------

::

  wget https://repo.continuum.io/miniconda/Miniconda3-latest-Linux-x86_64.sh -O miniconda.sh
  bash miniconda.sh -b -p $HOME/miniconda
  export PATH="$HOME/miniconda/bin:$PATH"
  git clone https://github.com/Open-EO/openeo-pg-parser-python.git
  cd openeo-pg-parser-python

2. Create the conda environment
-------------------------------

::

  conda env create -f conda_environment.yml

3. Install package in the conda environment
--------------------------------------------------------

::

  source activate openeo-pg-parser-python
  python setup.py install
  
Change 'install' with 'develop' if you plan to further develop the package.


Note
====

This project has been set up using PyScaffold 3.1. For details and usage
information on PyScaffold see https://pyscaffold.org/.
