⛔️ DEPRECATED
===============

This repository is no longer supported, please consider using alternatives.

.. image:: http://unmaintained.tech/badge.svg
  :target: http://unmaintained.tech
  :alt: No Maintenance Intended

CircuitPython Driver for the Bosch BMA423 accelerometer included in the lilygo watch


Dependencies
=============
This driver depends on:

* `Adafruit CircuitPython <https://github.com/adafruit/circuitpython>`_
* `Bus Device <https://github.com/adafruit/Adafruit_CircuitPython_BusDevice>`_
* `Register <https://github.com/adafruit/Adafruit_CircuitPython_Register>`_

Please ensure all dependencies are available on the CircuitPython filesystem.
This is easily achieved by downloading
`the Community Bundle library and driver bundle <https://circuitpython.org/libraries>`_
or individual libraries can be installed using
`circup <https://github.com/adafruit/circup>`_.


Installing from PyPI
=====================

On supported GNU/Linux systems like the Raspberry Pi, you can install the driver locally `from
PyPI <https://pypi.org/project/circuitpython-bma423/>`_.
To install for current user:

.. code-block:: shell

    pip3 install circuitpython-bma423

To install system-wide (this may be required in some cases):

.. code-block:: shell

    sudo pip3 install circuitpython-bma423

To install in a virtual environment in your current project:

.. code-block:: shell

    mkdir project-name && cd project-name
    python3 -m venv .venv
    source .env/bin/activate
    pip3 install circuitpython-bma423

Installing to a Connected CircuitPython Device with Circup
==========================================================

Make sure that you have ``circup`` installed in your Python environment.
Install it with the following command if necessary:

.. code-block:: shell

    pip3 install circup

With ``circup`` installed and your CircuitPython device connected use the
following command to install:

.. code-block:: shell

    circup install bma423

Or the following command to update an existing version:

.. code-block:: shell

    circup update

Usage Example
=============

Take a look at the examples directory

Documentation
=============
API documentation for this library can be found on `Read the Docs <https://circuitpython-bma423.readthedocs.io/>`_.


Contributing
============

Contributions are welcome! Please read our `Code of Conduct
<https://github.com/jposada202020/CircuitPython_/blob/HEAD/CODE_OF_CONDUCT.md>`_
before contributing to help this project stay welcoming.
