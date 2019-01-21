.. -*- mode: rst -*-

.. role:: bash(code)
   :language: bash

|Travis|_ |PyPi|_ |TestStatus|_ |PythonVersion|_

.. |Travis| image:: https://travis-ci.org/aagnone3/personal-capital-plus.svg?branch=master

.. |PyPi| image:: https://badge.fury.io/py/personal-capital-plus.svg
.. _PyPi: https://badge.fury.io/py/personal-capital-plus

.. |TestStatus| image:: https://travis-ci.org/aagnone3/personal-capital-plus.svg
.. _TestStatus: https://travis-ci.org/aagnone3/personal-capital-plus.svg

.. |PythonVersion| image:: https://img.shields.io/pypi/pyversions/personal-capital-plus.svg
.. _PythonVersion: https://img.shields.io/pypi/pyversions/personal-capital-plus.svg

personal-capital-plus
================

Personal Capital + Python = Pipelined personal finance

Use your existing Personal Capital login credentials to pull the JSON data directly, allowing
you to perform any custom analyses you wish to. The API calls can be found by viewing the HTTP
calls the browser makes after login.

.. _entry.py: personalcapital/tools/entry.py

This library pulls the data into a Mongo database to enable local analysis. See entry.py_.

Documentation
-------------

Documentation can be found at the github pages here_

.. _here: https://aagnone3.github.io/personal-capital-plus/

Dependencies
~~~~~~~~~~~~

personal-capital-plus is tested to work under Python 3.x.
See the requirements via the following command:

.. code-block:: bash

  cat requirements.txt

Installation
~~~~~~~~~~~~

personal-capital-plus is currently available on the PyPi's repository and you can
install it via `pip`:

.. code-block:: bash

  pip install -U personal-capital-plus

If you prefer, you can clone it and run the setup.py file. Use the following
commands to get a copy from GitHub and install all dependencies:

.. code-block:: bash

  git clone https://github.com/aagnone3/personal-capital-plus.git
  cd personal-capital-plus
  pip install .

Or install using pip and GitHub:

.. code-block:: bash

  pip install -U git+https://github.com/aagnone3/personal-capital-plus.git


Now, to avoid a 2FA prompt each run, set the following environment variables:

.. code-block:: bash

   export PEW_EMAIL=<your_personal_capital_email>
   export PEW_PASSWORD=<your_personal_capital_password>

With the environment defined, give it a whirl:

.. code-block:: bash

   # only available if you've installed it
   pc_api update

   # otherwise, use this
   PYTHONPATH=${PYTHONPATH:-}:${PWD} python personalcapital/tools/entry.py update

Local Testing
~~~~~~~~~~~~~

.. code-block:: bash

  make test
  
Travis Testing
~~~~~~~~~~~~~~

The :bash:`Makefile`, :bash:`.travis.yml` file and :bash:`.ci` directory contain the structure necessary to have Travis_ test the repository upon all branch updates. Some additional steps, however, are needed:

- Enable the repository to be monitored by Travis via your Travis profile.
- Generate a Github app token, and assign it to the (private) environment variable :bash:`${GITHUB_TOKEN}` in the Travis environment.

.. _Travis: https://travis-ci.org/aagnone3/personal-capital-plus
