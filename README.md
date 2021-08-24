virt-tuner is a tool modifying the libvirt XML definition of a virtual machine to optimize it
depending on a selected use case.

Dependencies
------------

 * python 3
 * python libvirt binding

Hacking
-------

To test changes without installing the package in your machine,
use the run script. For example to run virt-tuner, use a command
like the following one:

    PYTHONPATH=$PWD/src python3 -m virt_tuner --help

The following commands will be useful for anyone writing patches:

    tox                  # Run local unit test suite with coverage
    pytest               # Direct run of the test suite, usefull for debugging
    ./setup.py lint      # Run pylint and black against the codebase

Any patches shouldn't change the output of `tox` or `lint`. The `lint` requires `pylint` and `black` to be installed.
